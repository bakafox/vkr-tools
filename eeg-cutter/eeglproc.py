import mne
import numpy as np
from pathlib import Path
import psutil

from zoneutil import load_zones, create_reverse_map


class LazyEEGProcessor:
    def __init__(
            self,
            path_eeg,
            path_zones,
            bad_channels,
            output_dir='~cache_',
            safety_factor=0.5,
        ):
        self.filepath = Path(path_eeg)
        self.bad_channels = bad_channels
        self.output_dir = Path(output_dir + self.filepath.stem)
        self.safety_factor = safety_factor
        self.raw = None
        self.fwd = None
        self.inverse_operator = None
        self.lambda2 = None
        self.chunk_size = None
        self.current_chunk_id = 0
        self.stc = None

        self.zones = load_zones(path_zones)
        self.reverse_zones = create_reverse_map(self.zones)

        self._init_processing_environment()

    def _init_processing_environment(self):
        # Не загружаем данные в память целиком, только метаданные
        self.raw = mne.io.read_raw_eeglab(self.filepath, preload=False)

        if self.bad_channels:
            self.raw.drop_channels(self.bad_channels)

        # T = [[1., 0., 0., 0.],
        #      [0., 1., 0., 0.],
        #      [0., 0., 1., 0.],
        #      [0., 0., 0., 1.]]

        # Используем среднее по всем электродам в качестве второго
        # значения для вычисления разности потенциалов между точками
        self.raw.set_eeg_reference('average', projection=True)

        # Путь до усреднённой анатомической модели вершин мозга
        fs_dir = mne.datasets.fetch_fsaverage(verbose=True)
        src_file = fs_dir / 'bem' / 'fsaverage-ico-5-src.fif'

        # Вычисление форвард-модели (соотношения между зарегистрированной
        # электродами активностью и ранее загруженными вершинами; "если в
        # точке X есть активность, что мы увидим на каждом электроде?")
        self.fwd = mne.make_forward_solution(
            self.raw.info,
            trans='fsaverage',
            src=src_file,
            bem=fs_dir / 'bem' / 'fsaverage-5120-5120-5120-bem-sol.fif',
            meg=False,
            eeg=True,
            mindist=5.0,
            n_jobs=4
        )

        # Убираем дубликаты вершин среди источников, сохраняя координаты
        self.aligned_vertices, self.aligned_indices = self._align_vertices(
            self.fwd['source_rr'], precision=10**4
        )

        # Для каждой вершины определяем, к какой зоне она относится
        self.zone_texture = self._build_zone_texture()

        # Считаем матрицу ковариации шума (математическое описание, как "шумят"
        # электроды). Нужна для построения обратного оператора ("если мы видим
        # такой-то сигнал на электродах, где в мозгу может находиться источник?")
        noise_cov = mne.compute_raw_covariance(self.raw)
        self.inverse_operator = mne.minimum_norm.make_inverse_operator(
            self.raw.info, self.fwd, noise_cov, loose=0.2, depth=0.8
        )

        # Параметры sLORETA
        snr = 3.0
        self.lambda2 = 1.0 / snr ** 2

        # Выполняем автоматический расчет размера чанка
        self._calculate_optimal_chunk_size()

    def _build_zone_texture(self):
        # Получаем список всех ЭЭГ-каналов
        picks = mne.pick_types(self.raw.info, eeg=True, exclude=[])
        ch_names = [self.raw.info['ch_names'][p] for p in picks]

        n_src = self.fwd['nsource']
        row_names = self.fwd['sol']['row_names']
        row_name_set = {name: i for i, name in enumerate(row_names)}

        # Берём только каналы, которые есть И в данных ЭЭГ, И в форвард-модели
        # (некоторые каналы могут отсутствовать во взятых заранее вершинах)
        fwd_picks = []
        valid_ch_names = []
        for ch in ch_names:
            if ch in row_name_set:
                fwd_picks.append(row_name_set[ch])
                valid_ch_names.append(ch)

        G = self.fwd['sol']['data'][fwd_picks, :]

        # Количество ориентаций на источник: 3 (свободная ориентация) или 1 (фиксированная)
        n_ori = G.shape[1] // n_src

        # Получаем матрицу силы влияния канала на источник (n_каналов * n_источников)
        if n_ori > 1:
            G = np.linalg.norm(G.reshape(len(fwd_picks), n_src, n_ori), axis=2)

        # Для каждого источника находим, какой канал влияет на него сильнее всего,
        # затем берём имя этого канала, ищем в reverse_zones и получаем номер зоны
        dominant_ch_idx = np.argmax(np.abs(G), axis=0)
        zone_texture = np.zeros(n_src, dtype=int)
        for src_i, ch_i in enumerate(dominant_ch_idx):
            ch_name = ch_names[ch_i].lower()
            zone_texture[src_i] = self.reverse_zones.get(ch_name, 0)

        return zone_texture[self.aligned_indices] # Возвращаем только уникальные вершины

    def _calculate_optimal_chunk_size(self):
        # Узнаём, сколько RAM сейчас свободно, и берём "безопасную" часть
        available_mem = psutil.virtual_memory().available * self.safety_factor

        # Обрабатываем ровно 1 кадр и смотрим, сколько байт занимает результат
        test_stc = self._process_chunk(0, 1)
        mem_per_frame = test_stc.data.nbytes

        self.chunk_size = max(1, int(available_mem // mem_per_frame))
        print(f'\n=== Оптимальный размер чанков: {self.chunk_size} кадров. ===\n')

    def _get_chunk_filename(self, start: int, stop: int) -> Path:
        return self.output_dir / f'chunk_{start}_{stop}.npy'

    def _process_chunk(self, start: int, stop: int) -> mne.SourceEstimate:
        # Применяем обратный оператор к отрезку сырых данных методом sLORETA.
        # Это стандартизированный вариант метода минимальных норм, являющийся
        # нечувствительным к глубине источника. Через pick_ori='normal' берём
        # только компоненту активности, перпендикулярную поверхности коры
        stc = mne.minimum_norm.apply_inverse_raw(
            self.raw, self.inverse_operator, self.lambda2,
            method='sLORETA', pick_ori='normal',
            start=start, stop=stop
        )
        return stc
    
    def _check_new_chunk(self, frame_id: int):
        # По номеру кадра определяем, в каком чанке он находится
        # (например, при chunk_size=100 кадр 250 будет в чанке №2),
        # и смотрим, нужен ли для получения кадра другой чанк
        chunk_id = frame_id // self.chunk_size

        # Если запрошенный кадр не в текущем чанке, загружаем новый
        if self.current_chunk_id != chunk_id or self.stc is None:
            start = chunk_id * self.chunk_size
            stop = min((chunk_id + 1) * self.chunk_size, self.get_frames_len())

            filename = self._get_chunk_filename(start, stop)

            # Если чанк уже есть в кэше, грузим оттуда
            if filename.exists():
                print(f'\n=== Cache-Hit чанка {start} -- {stop}. ===\n')
                return np.load(filename.absolute().as_posix())

            # Если нет, обрабатываем и сохраняем новый чанк
            self.stc = self._process_chunk(start, stop)
            print(f'\n=== Кэширован новый чанк {start} -- {stop}. ===\n')

            # TODO: у меня на компе работает медленно, потестить,
            # мб заменить на другой способ сохранения чанков
            filename.parent.mkdir(parents=True, exist_ok=True)
            np.save(filename.absolute().as_posix(), self.stc.data)

            self.current_chunk_id = chunk_id

    def _align_vertices(self, vertices, precision: int = 10**5):
        # Форвард-модель может содержать несколько источников с очень
        # близкими координатами (из-за ошибок округления). Поэтому
        # проводим квантизацию координат и удаляем дубликаты вершин
        vertices, indices = np.unique(
            ((vertices * precision).round() / precision),
            axis=0, return_index=True
        )
        return vertices * 30, indices

    def __len__(self) -> int:
        return np.ceil(self.raw.n_times / self.chunk_size).astype(int)

    def __getitem__(self, frame_id: int) -> tuple[np.typing.NDArray, list]:
        # Получение чанка по индексу с lazy-вычислениями
        self._check_new_chunk(frame_id)
        return self.stc.data[
            self.aligned_indices,
            frame_id % self.chunk_size
        ], self.aligned_vertices

    def get_frames_len(self) -> int:
        return self.raw.n_times

    def get_freq(self) -> float:
        return float(self.raw.info['sfreq'])

    def get_events(self):
        return mne.events_from_annotations(self.raw)

    def stream(self) -> tuple[np.typing.NDArray, list]:
        # Генератор для потоковой ленивой обработки
        total_frames = self.get_frames_len()
        for i in range(0, total_frames):
            # функция "засыпает" после возвращения каждого кадра
            # и продолжает с того же места при следующем вызове
            yield self[i]

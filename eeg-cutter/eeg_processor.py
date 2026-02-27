import mne
import numpy as np
from pathlib import Path
import psutil
import hashlib
import nibabel as nib
from nilearn import surface


class LazyEEGProcessor:
    def __init__(self, filepath, bad_channels, output_dir='processed_chunks_', safety_factor=0.5):
        self.filepath = Path(filepath)
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
        self.fwd = None
        self._init_processing_environment()

    def project(self, volume, surfaces, radius=0.0, n_samples=20, interpolation='linear', kind='linear'):
        results = {}
        for name, path in surfaces.items():
            try:
                results[name] = surface.vol_to_surf(
                    volume,
                    path,
                    kind=kind,
                    radius=radius,
                    interpolation=interpolation,
                    n_samples=n_samples
                )
            except ValueError:
                print('\n=== Не найдено ни одной точки для построения проекции. ===\n')

        full_data = np.zeros_like(results['pial'])
        for vertex in range(len(full_data)):
            votes = [results[name][vertex] for name in results]
            non_zero = [v for v in votes if v > 0]
            if non_zero:
                full_data[vertex] = np.bincount(non_zero).argmax()
        return full_data

    def _init_processing_environment(self):
        self.i = 0

        self.raw = mne.io.read_raw_eeglab(self.filepath, preload=False)

        if self.bad_channels:
            self.raw.drop_channels(self.bad_channels)

        self.raw.set_eeg_reference('average', projection=True)

        # Загрузка форвард-модели
        fs_dir = mne.datasets.fetch_fsaverage(verbose=True)
        src_file = fs_dir / 'bem' / 'fsaverage-ico-5-src.fif'

        # T = [[1., 0., 0., 0.],
        #      [0., 1., 0., 0.],
        #      [0., 0., 1., 0.],
        #      [0., 0., 0., 1.]]
        
        brodmann_map = nib.load('brodmann.nii')
        # lh_full_data = surface.vol_to_surf(brodmann_map, fs_dir / 'surf' / 'lh.pial', radius=0.0, interpolation='nearest', kind='ball', n_samples=160)
        # rh_full_data = surface.vol_to_surf(brodmann_map, fs_dir / 'surf' / 'rh.pial', radius=0.0, interpolation='nearest', kind='ball', n_samples=160)

        surfaces_lh = {
            'pial': fs_dir / 'surf' / 'lh.pial',
            'white': fs_dir / 'surf' / 'lh.white',
            'inflated': fs_dir / 'surf' / 'lh.inflated'
        }
        surfaces_rh = {
            'pial': fs_dir / 'surf' / 'rh.pial',
            'white': fs_dir / 'surf' / 'rh.white',
            'inflated': fs_dir / 'surf' / 'rh.inflated'
        }

        lh_full_data = self.project(brodmann_map, surfaces_lh, n_samples=160, kind='ball')
        rh_full_data = self.project(brodmann_map, surfaces_rh, n_samples=160, kind='ball')

        src = mne.read_source_spaces(src_file)

        left_vertno = src[0]['vertno']
        right_vertno = src[1]['vertno']

        self.brodmann_texture = np.concatenate([lh_full_data[left_vertno], rh_full_data[right_vertno]])

        self.fwd = mne.make_forward_solution(
            self.raw.info,
            trans='fsaverage',
            src=src_file,
            bem=fs_dir / 'bem' / 'fsaverage-5120-5120-5120-bem-sol.fif',
            meg=False, eeg=True,
            mindist=5.0,
            n_jobs=4
        )

        self.aligned_vertices, self.aligned_indices = self._align_vertices(self.fwd['source_rr'], precision=10**4)
        self.brodmann_texture = self.brodmann_texture[self.aligned_indices]

        # Создание обратного оператора
        noise_cov = mne.compute_raw_covariance(self.raw)
        self.inverse_operator = mne.minimum_norm.make_inverse_operator(
            self.raw.info, self.fwd, noise_cov, loose=0.2, depth=0.8
        )

        # Параметры sLORETA
        snr = 3.0
        self.lambda2 = 1.0 / snr ** 2

        # Выполняем автоматический расчет размера чанка
        self._calculate_optimal_chunk_size()

    def _calculate_optimal_chunk_size(self):
        available_mem = psutil.virtual_memory().available * self.safety_factor
        test_stc = self._process_chunk(0, 1)
        mem_per_frame = test_stc.data.nbytes
        self.chunk_size = max(1, int(available_mem // mem_per_frame))
        print(f'\n=== Оптимальный размер чанков: {self.chunk_size} кадров. ===\n')

    def _get_chunk_filename(self, start, stop):
        hash_key = f'{self.filepath.stem}_{start}_{stop}'
        return self.output_dir / f'{hashlib.md5(hash_key.encode()).hexdigest()}.npy'

    def _process_chunk(self, start, stop):
        
        stc = mne.minimum_norm.apply_inverse_raw(
            self.raw, self.inverse_operator, self.lambda2,
            method='sLORETA', pick_ori='normal',
            start=start, stop = stop
        )

        return stc

    def get_frames_len(self):
        return self.raw.n_times

    def __len__(self):
        return np.ceil(self.raw.n_times / self.chunk_size).astype(int)

    def _align_vertices(self, vertices, precision=10 ** 5):
        vertices, indices = np.unique(((vertices * precision).round() / precision), axis=0, return_index=True)
        vertices *= 30
        return vertices, indices

    def get_freq(self):
        return float(self.raw.info['sfreq'])
    
    def get_events(self):
        return mne.events_from_annotations(self.raw)

    # LEGACY
    def _getitem(self, index):
        start = index * self.chunk_size
        stop = (index + 1) * self.chunk_size
        filename = self._get_chunk_filename(start, stop)

        # Если чанк уже существует
        if filename.exists():
            return np.load(filename.absolute().as_posix())

        # Если чанк не существует - вычисляем и сохраняем
        stc, fwd = self._process_chunk(start, stop)
        np.save(filename.absolute().as_posix(), stc.data)
        self.current_chunk_id = index
        return stc.data, fwd

    def _check_new_chunk(self, frame_id):
        chunk_id = frame_id // self.chunk_size
        if self.current_chunk_id != chunk_id or self.stc is None:
            start = chunk_id * self.chunk_size
            stop = min((chunk_id + 1) * self.chunk_size, self.get_frames_len())

            filename = self._get_chunk_filename(start, stop)

            # Если чанк уже существует
            if filename.exists():
                return np.load(filename.absolute().as_posix())

            self.stc = self._process_chunk(start, stop)
            # TODO: у меня на компе работает медленно, потестить, мб заменить на другой способ сохранения чанков
            # np.save(filename.absolute().as_posix(), self.stc.data)
            self.current_chunk_id = chunk_id

    def __getitem__(self, frame_id):
        # Получение чанка по индексу с lazy-вычислениями
        self._check_new_chunk(frame_id)
        return self.stc.data[self.aligned_indices, frame_id % self.chunk_size], self.aligned_vertices

    def stream(self):
        # Генератор для потоковой ленивой обработки
        total_frames = len(self.raw.n_times)
        for i in range(0, total_frames):
            yield self[i]

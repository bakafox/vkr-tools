from typing import List
from mne._fiff.meas_info import Info
from mne.io.eeglab.eeglab import RawEEGLAB
from mne.channels.montage import DigMontage

from pathlib import Path
import click
import numpy as np
import pandas as pd
import mne


def read_eeg(
    path_set: Path,
    n_ch: int
) -> RawEEGLAB:
    eeg_raw = mne.io.read_raw_eeglab(path_set, preload=True)

    inf: Info = eeg_raw.info
    bad_chs = []

    # Проверяем совпадение по числу каналов, затем отсеиваем битые
    if len(inf['chs']) != n_ch:
        print(f'Кол-во каналов ({len(inf['chs'])}) не соответствует ожидаемому ({n_ch}).')
        exit(-1)

    for ch in inf['chs']:
        # Первые 3 значения в loc нас интересуют больше всего
        if np.any(np.isnan(ch['loc'][:3])):
            bad_chs.append(ch['ch_name'])

    if bad_chs:
        print(f'Удаление каналов с некорректными координатами: \n{bad_chs}')
        eeg_raw.drop_channels(bad_chs)
    
    return eeg_raw


def get_montage(
    eeg_chs,
    std_montage_kind: str,
) -> DigMontage:
    # Сперва создаём стандартную карту расположений электродов
    std_montage = mne.channels.make_standard_montage(std_montage_kind)

    # Индексы каналов, которые есть и в карте, и в нашем ЭЭГ
    new_ch_idx = [
        i for (i, ch) in enumerate(std_montage.ch_names) if ch in eeg_chs
    ]
    print(f'Найдено {len(new_ch_idx)} точек электродов из {len(std_montage.ch_names)} возможных.')

    # Теперь на её основе создаём карту электродов, в которой
    # есть только те электроды, которые изначально были у нас
    new_ch_names = [std_montage.ch_names[i] for i in new_ch_idx]

    new_electrodes = (
        std_montage.dig[0:3] # Электроды-точки базисного отсчёта
        + [std_montage.dig[i+3] for i in new_ch_idx]
    )

    new_montage = DigMontage(
        ch_names=new_ch_names,
        dig=new_electrodes
    )

    return new_montage


def get_zone(
    ch: str,
) -> str:
    # Деление каналов именно на такие зоны взято из файлов Ши Хаонаня!
    # Также при построении отчасти использовалась эта публикация:
    # https://www.researchgate.net/publication/380786384_Differences_in_Electroencephalography_Power_Levels_between_Poor_and_Good_Performance_in_Attentional_Tasks

    if ch in ['lpa', 'rpa', 'nasion']:
        return 'ref' # Референсные каналы типа

    if ch.startswith('F') or ch.startswith('AF'): # F, FC, Fp, FT
        try:
            cnum = int(ch[-1]) # Осторожно, хрупкий код!
            return 'LF' if (cnum % 2 != 0) else 'RF'

        except Exception: # Fz, FCz, FPz, ...
            return 'MF'
    
    if ch.startswith('C') or ch.startswith('T'): # C, CP, T
        try:
            cnum = int(ch[-1]) # Осторожно, хрупкий код!
            return 'LT' if (cnum % 2 != 0) else 'RT'

        except Exception: # Cz, CPz, Tz, ...
            return 'MC'
    
    if ch.startswith('P') or ch.startswith('O'): # P, PO, O
        try:
            cnum = int(ch[-1]) # Осторожно, хрупкий код!
            return 'LP' if (cnum % 2 != 0) else 'RP'

        except Exception: # Pz, POz, Oz, ...
            return 'MP'
    
    return '???'


def save_channels(
    montage: DigMontage,
    path_out: Path
) -> None:
    # Распаковка карты в список координат
    pos = montage.get_positions()

    rows = [
        np.append([ch], pos['ch_pos'][ch]) for ch in montage.ch_names
    ]

    # Не забываем про электроды-точки базисного отсчёта!
    rows = [
        np.append([b_ch], pos[b_ch]) for b_ch in ['nasion', 'lpa', 'rpa']
    ] + rows

    df = pd.DataFrame(rows, columns=['name', 'x', 'y', 'z'])
    df.to_csv(path_out, index=False)


def save_zones(
    montage: DigMontage,
    path_out: Path
) -> None:
    # Берём названия каналов из карты
    chs = montage.ch_names

    df = pd.DataFrame({'channel': chs})
    df['zone'] = df['channel'].apply(get_zone)

    # Делаем группировочный DataFrame для подсчёта числа вхождений
    df_zone_cnt = df.groupby('zone', as_index=False).count()

    df_zone_cnt.columns = ['zone', 'n_ch']
    df_zone_cnt.to_csv(path_out, index=False)



@click.command(name='MAT Python Opener & Converter, 26-01-17')
@click.option('-i', required=True, type=str,
    help='Путь до входного файла set. В папке с ним также должен быть одноимённый файл fdt!'
)
@click.option('-o', default='./', type=str,
    help='Путь до выходного csv, без имени. Если такой файл уже есть, он будет перезаписан.'
)
@click.option('-c', default=48, type=int,
    help='Ожидаемое количество каналов в файле ЭЭГ.'
)
def start(i, o, c):
    try:
        eeg = read_eeg(Path(i), c)

        if eeg.info['dig'] is not None:
            print("Используем координаты из файла")
            montage = eeg.get_montage()
        else:
            print("Координат нет, используем стандартный шаблон")
            montage = get_montage(eeg.ch_names, 'standard_1020')

        csv_channels = Path(i).name.split('.')[0] + '_ch.csv'
        save_channels(montage, Path(o) / csv_channels)

        csv_zones = Path(i).name.split('.')[0] + '_z.csv'
        save_zones(montage, Path(o) / csv_zones)

        print('Конвертация успешно завершена!')
        exit(0)

    except Exception as e:
        print('ОШИБКА:', e)
        exit(-1)


if __name__ == '__main__':
    start()

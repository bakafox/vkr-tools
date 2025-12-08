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
        if np.isnan(ch['loc'][0] or ch['loc'][1] or ch['loc'][2]):
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


def save_pos(
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


@click.command(name='MAT Python Opener & Converter, 25-12-09')
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
        eeg = read_eeg(
            Path(i),
            c
        )

        montage = get_montage(
            eeg.ch_names,
            'standard_1005'
        )

        csv_name = Path(i).name.split('.')[0] + '.csv'
        save_pos(
            montage,
            Path(o) / csv_name
        )

        print('Конвертация успешно завершена!')
        exit(0)

    except Exception as e:
        print('ОШИБКА:', e)
        exit(-1)


if __name__ == '__main__':
    start()

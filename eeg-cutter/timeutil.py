from PyQt5.QtCore import QTime


def time_str_to_int(time_str: str, freq: float) -> int:
    time = QTime.fromString(time_str, 'hh:mm:ss:zzz')

    return int(
        (((time.hour() * 24 + time.minute()) * 60 + time.second()) * 1000 + time.msec())
        * freq / 1000
    )

def time_int_to_str(time_int: int, freq: float) -> str:
    total = int(time_int * 1000 / freq)

    msec = total % 1000
    total //= 1000
    
    seconds = total % 60
    total //= 60

    minutes = total % 60
    hours = total // 60

    time = QTime(hours, minutes, seconds, msec)
    return time.toString('hh:mm:ss:zzz')

import gpsd
import pandas as pd

from os import path, remove
from datetime import datetime as dt, UTC, timedelta
from time import sleep, time
from glob import glob

def write_header():
    filename = dt.now(UTC).strftime('%Y%m%d_%H%M%S.csv')
    with open(filename, 'w') as f:
        f.write('time,latitude,longitude,altitude\n')
    return filename

def compress_old():
    now = dt.now(UTC)
    current_files = glob('*.csv')
    if path.exists('old.parquet'):
        all_data = pd.read_parquet('old.parquet')
    else:
        all_data = pd.DataFrame(columns=['time', 'latitude', 'longitude', 'altitude'])
    for file in current_files:
        this_data = pd.read_csv(file, parse_dates=['time'])
        all_data = pd.concat([all_data, this_data])
    all_data = all_data[all_data['time'] > now - timedelta(days=30)]
    all_data.to_parquet('old.parquet', index=False, compression='brotli')
    [remove(cf) for cf in current_files]


if __name__ == '__main__':
    compress_old()
    gpsd.connect()
    filename = None
    while True:
        sleep_time = 5 - (time() % 5)
        sleep(sleep_time)
        try:
            packet = gpsd.get_current()
            lat, lon = packet.position()
            alt = packet.altitude()
            timestamp = dt.now(UTC).replace(microsecond=0).isoformat()
            if filename is None:
                filename = write_header()
            with open(filename, 'a') as f:
                f.write(f'{timestamp},{lat},{lon},{alt}\n')
        except (gpsd.NoFixError, AttributeError):
            # No fix available yet
            print(f"{datetime.utcnow().isoformat()}: Waiting for GPS fix...")

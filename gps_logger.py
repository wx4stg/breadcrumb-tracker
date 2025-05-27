import gpsd
from os import path, remove
from datetime import datetime as dt, UTC, timedelta
from time import sleep, time
from glob import glob

if __name__ == '__main__':
    now = dt.now(UTC)
    current_files = glob('*.csv')
    [remove(cf) for cf in current_files if (now - dt.strptime(cf, '%Y%m%d_%H%M%S.csv').replace(tzinfo=UTC)) > timedelta(days=15)]
    gpsd.connect()
    filename = dt.now(UTC).strftime('%Y%m%d_%H%M%S.csv')
    with open(filename, 'w') as f:
        f.write('time,latitude,longitude,altitude\n')
    while True:
        sleep_time = 5 - (time() % 5)
        sleep(sleep_time)
        try:
            packet = gpsd.get_current()
            lat, lon = packet.position()
            alt = packet.altitude()
            timestamp = dt.now(UTC).replace(microsecond=0).isoformat()
            with open(filename, 'w') as f:
                f.write(f'{timestamp},{lat},{lon},{alt}\n')
        except (gpsd.NoFixError, AttributeError):
            # No fix available yet
            print(f"{datetime.utcnow().isoformat()}: Waiting for GPS fix...")

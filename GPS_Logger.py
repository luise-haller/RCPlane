import os
from datetime import datetime, timezone
import csv
from pymavlink import mavutil # pip install pymavlink pandas

GPS_DIR = os.path.expanduser("~/Data/GPS")
os.makedirs(GPS_DIR, exist_ok=True)

def setup_mavlink():
    connection = mavutil.mavlink_connection(
        '/dev/serial0', # or ttyAMA0
        baud=57600, #if i remember correctly
        autoreconnect=True
    )
    connection.wait_heartbeat()
    return connection

def log_gps():
    mav = setup_mavlink()
    current_date = datetime.now(timezone.utc).strftime('%Y%m%d')
    csv_path = os.path.join(GPS_DIR, f"gps_{current_date}.csv")

    with open(csv_path, 'a', newline="") as f:
        wr = csv.writer(f)
        if os.stat(csv_path).st_size == 0:
            wr.writerow(['timestamp','lat','lon','alt'])
        
        while True:
            mes = mav.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
            if mes:
                timestamp = datetime.now(timezone.utc).isoformat()  
                lat = mes.lat / 1e7
                lon = mes.lon / 1e7
                alt = mes.alt / 1e3
                wr.writerow([timestamp, lat, lon, alt])
                f.flush()


if __name__ == "__main__":
    log_gps()

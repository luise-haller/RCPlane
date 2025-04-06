import os
import pandas as pd # pip install pandas
from datetime import datetime, timezone

GPS_DIR = os.path.expanduser("~/Data/GPS")

def find_closest_gps(target_time):
    # finding the nearest GPS coords for a given utc timestamo
    gps_files = sorted(
        [f for f in os.listdir(GPS_DIR) if f.startswith('gps') and f.endswith('.csv')],
        reverse=True  # makes so you always use the most recent file first
    )
    
    if not gps_files:
        return {'lat': None, 'lon': None}

    try:
        # loading most recent
        df = pd.read_csv(
            os.path.join(GPS_DIR, gps_files[0]),
            parse_dates=['timestamp'],
            date_parser=lambda x: pd.to_datetime(x, utc=True)
        )
        if target_time.tzinfo is None:
            target_time = target_time.replace(tzinfo=timezone.utc) # to make sure that target_time = timezone aware
        
        # nearest timestamp
        time_diff = abs(df['timestamp'] - target_time)
        closest_idx = time_diff.idxmin()
        
        return {
            'lat': df.iloc[closest_idx]['lat'],
            'lon': df.iloc[closest_idx]['lon']
        }
    
    except Exception as e:
        print(f"GPS lookup error: {str(e)}")
        return {'lat': None, 'lon': None}

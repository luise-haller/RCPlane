import os
from datetime import datetime, timezone
import time
import csv
import subprocess
from gps_utils import find_closest_gps

output_dir = os.path.expanduser("~/Videos")
os.makedirs(output_dir, exist_ok="True")

duration_of_vid = 300 # 5mins

# Records 5min videos continously and saves them in the Videos dir
def record_vid():
    while True:
        start_time = datetime.now(timezone.utc)
        timestamp = start_time.strftime("%Y-%m-%d_%H-%M-%S")
        fname = f"{timestamp}.mp4"
        fpath = os.path.join(output_dir, fname)

        vid_record_command = [
            "libcamera-vid",
            "-t", str(duration_of_vid * 1000),
            "--codec", "libav", # encodes it properly so it can played on vlc
            "-o", fpath
        ]

        print("Filepath saved to is: " + fpath)
        subprocess.run(vid_record_command, check=True)

        end_time = datetime.now(timezone.utc)
        log_video_metadata(fname, start_time, end_time)

def log_video_metadata(fname, start, end):
    manifest_path = os.path.join(output_dir, "video_manifest.csv")
    header = not os.path.exists(manifest_path)

    with open(manifest_path, 'a') as f:
        wr = csv.writer(f)
        if header:
            wr.writerow(['filename','start_utc','end_utc','start_lat','start_lon'])
        
        # getting the gps that lies closests to the start + end times
        gps_coord = find_closest_gps(start)
        wr.writerow([fname, start.isoformat(), end.isoformat(), 
                       gps_coord['lat'], gps_coord['lon']])
        
if __name__ == "__main__":
    try:
        record_vid()
    except KeyboardInterrupt:
        print("\nRecording stopped.")

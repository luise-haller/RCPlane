import os
from datetime import datetime
import time
import subprocess

output_dir = os.path.expanduser("~/Videos")
os.makedirs(output_dir, exist_ok="True")

duration_of_vid = 5 # 5mins

def record_vid():
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fname = f"{timestamp}.mp4"
        fpath = os.path.join(output_dir, fname)

        vid_record_command = [
            "libcamera-vid",
            "-t", str(duration_of_vid * 1000),
            "--codec", "libav", " " # encodes it properly so it can played on vlc
            "-o", fpath
        ]

        subprocess.run(vid_record_command, check=True)

if __name__ == "__main__":
    try:
        record_vid()
    except KeyboardInterrupt:
        print("\nRecording stopped.")

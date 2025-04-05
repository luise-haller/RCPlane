"""
PMS5003 Data Log Script

This script reads data from the PMS5003 sensor connected to a Raspberry Pic 4B,
and logs the data to a CSV file.

Hardware Setup:
- PMS5003 Sensor:
    - VCC -> 5V GPIO pin
    - GND -> GND GPIO pin
    - TX -> RXD (GPIO 15)

Transport Protocol:
- Default baud rate: 9600
- Data packet size: 32 bytes
- Structure:
    - Start characters: 0x42, 0x4d (fixed)
    - Frame length: 2bytes - high+low
    - Data fields:
        - Dat1: PM1.0 concentration (CF=1, standard particle)
        - Dat2: PM2.5 concentration (CF=1, standard particles)
        - Dat3: PM10 concentration (CF=1, standard particles)
        - Dat4: PM1.0 concentration (under atmospheric environment)
        - Dat5: PM2.5 concentration (under atmospheric environment)
        - Dat6: PM10 concentration (under atmospheric environment)
        - Dat7-12: Particle counts for diameters: >0.3µm, >0.5µm, >1.0µm, >2.5µm, >5.0µm, >10µm in 0.1L of air
        - Dat13: Reserved
    - Check code: Sum of all previous bytes, retaining only the lower 8 bits

Libraries:
- pms5003 ('pip install pms5003')
- csv

1. Make sure sensor is installed as described above.
2. Make sure script is placed in the correct dir ('~/Automation_Scripts')
3. Run script using 'python3 PM_Sensor_Data.py'
4. After successful run, data is logged to a CSV file in ~/Data
"""

import time
from datetime import datetime
import csv
import os
from pms5003 import PMS5003

DAT_DIR = "~/Data/"
CSV_FNAME = "pms5003_data.csv"
LOGGING_INTV = 1
MAV_FILE_SIZE = 1 * 1024 * 1024 # 1MB before rotating files; enough for 30min flight while efficient

os.makedirs(DAT_DIR, exist_ok=True)

# use "raspi-config" to enable serial, or add
# "dtoverlay=uart0" to /boot/config.txt check!!

# configuring the sensor
pms5003 = PMS5003 (
    device='/dev/', #figure out serial port...either ttyAMA0 or serial0
    baudrate=9600,
    pin_enable="GPIO22", #if we stick with rpi4
    pin_reset="GPIO27"
)

def get_csv_path():
    base_path = os.path.join(DAT_DIR, CSV_FNAME)

    if os.path.exists(base_path) and os.path.getsize(base_path) > MAV_FILE_SIZE:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(DAT_DIR, f"pms5003_data_{timestamp}.csv")
    return base_path

def init_csv_file(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'timestamp',
                'pm1_0_std', 'pm2_5std', 'pm10_std',
                'pm1_0_atm', 'pm2_5_atm', 'pm10_atm',
                'particles_0_3um', 'particles_0_5um', 'particles_1_0um',
                'particles_2_5um', 'particles_5_0um', 'particles_10_0um'
            ])
    return file_path

def append_to_csv(file_path, dat):
    with open(file_path, 'a', newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            datetime.now().isoformat(),
            dat.pm_ug_per_m3(1.0, True),
            dat.pm_ug_per_m3(2.5, True),
            dat.pm_ug_per_m3(10, True),
            dat.pm_ug_per_m3(1.0, False), 
            dat.pm_ug_per_m3(2.5, False), 
            dat.pm_ug_per_m3(10, False),
            dat.pm_per_1l_air(0.3), 
            dat.pm_per_1l_air(0.5), 
            dat.pm_per_1l_air(1.0),
            dat.pm_per_1l_air(2.5), 
            dat.pm_per_1l_air(5), 
            dat.pm_per_1l_air(10)
        ])

def main():
    print("Starting pms5003 data collection")

    csvf = init_csv_file(get_csv_path())

    try:
        while True:
            try:
                dat = pms5003.read()
                csvf = init_csv_file(get_csv_path()) # rotating file if required
                append_to_csv(csvf, dat)

                print(f"[{datetime.now().isoformat()}] PM2.5: {dat.pm_ug_per_m3(2.5, False)} µg/m³")
                time.sleep(LOGGING_INTV)
            except Exception as e:
                print(f"Error reading sensor: {e}")
                time.sleep(1)
    except KeyboardInterrupt:
        print("Sensor reading interrupted.")
        print("Closing the program")

if __name__ == "__main__":
    main()

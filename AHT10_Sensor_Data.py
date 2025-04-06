"""
AHT10 Humidity and Temperator Sensor Logging

This script reads data from the AHT10 sensor connected to a Raspberry Pi 4B,
and logs the data to a CSV file.

Notes:
    1. Enable I2C with 'sudo raspi-config' -> interface options -> i2c -> enable
        - to verify 'sudo i2cdetect -y 1' must only have 0x38 address

Libraries: 
- 'pip install smbus2'

Hardware Setup:
- AHT10 Sensor:
    - VCC -> 3.3V (GPIO 1)
    - GND -> GND
    - SDA -> GPIO 2 (SDA)
    - SCL -> GPIO 3 (SCL)
"""
import time
from datetime import datetime
import smbus2
import os

class AHT10:
    def __init__(self, bus=1, address=0x38):
        self.bus = smbus2.SMBus(bus)
        self.address = address
        self.init_sensor()
        
    def init_sensor(self):
        try:
            # soft resetting
            self.bus.write_byte(self.address, 0xBA)
            time.sleep(0.02)

            # actual init
            self.bus.write_i2c_block_data(self.address, 0xE1, [0x08, 0x00]) 
            time.sleep(0.01)

            # calibration status
            status = self.bus.read_byte(self.address)
            if not (status & 0x08):
                raise RuntimeError("Calibration failed")
            
        except Exception as e:
            self.bus.close()
            raise e
        
    def read_dat(self):
        # triggering measurements
        self.bus.write_i2c_block_data(self.address, 0xAC, [0x33, 0x00])
        time.sleep(0.1)

        dat = self.bus.read_i2c_block_data(self.address, 0x00, 6)

        raw_humidity = ((dat[1] << 16) | (dat[2] << 8) | dat[3]) >> 4
        raw_temp = ((dat[3] & 0x0F) << 16) | (dat[4] << 8) | dat[5]

        # converting
        humidity = (raw_humidity / 1048576) * 100
        temp = (raw_temp / 1048576) * 200 - 50

        return round(temp, 1), round(humidity, 1)
    

def log_to_csv(dir="~/Data", max_file_size=5 * 1024 * 1024, interval=10):
    sensor = AHT10(bus=1)
    dir = os.path.expanduser(dir)
    os.makedirs(dir, exist_ok=True)

    def get_new_fname():
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join(dir, f"sensor_data_{timestamp}.csv")
    
    fname = get_new_fname()

    with open(fname, 'w') as f:
        f.write("Timestamp,Temperature (C),Humidity (%)\n") # header
    
    while True:
        try:
            temp, hum = sensor.read_data()
            timestamp = datetime.now().isoformat()
            
            with open(fname, 'a') as f:
                f.write(f"{timestamp},{temp},{hum}\n")
                f.flush()
            
            # roate file if file size too big
            if os.path.getsize(fname) >= max_file_size:
                fname = get_new_fname()
                
                with open(fname, 'w') as f:
                    f.write("Timestamp,Temperature (C),Humidity (%)\n")  # rewriting header when rotating
                
            time.sleep(interval)
    
        except KeyboardInterrupt:
            sensor.bus.close()
            print("\nLogging was stopped")
            break
        
        except Exception as e:
            print(f"Error: {str(e)}")
            time.sleep(1)

        
if __name__ == "__main__":
   log_to_csv()

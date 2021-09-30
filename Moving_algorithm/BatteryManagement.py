import sys
import re
import threading
import time
import subprocess
from Thread import *
distro_id_line_pattern = "Distributor ID:.+?(?=n)."
process = subprocess.Popen(["lsb_release", "-a"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
host_sys_info = process.communicate()
OS_ID_LINE = re.findall(distro_id_line_pattern, str(host_sys_info[0]))
distro_ID = OS_ID_LINE[0].replace("Distributor ID:\\t", '')
distro_ID = distro_ID.replace("\\n", '')
if distro_ID == "Raspbian":
    from ADS7830 import *
    from Led import *



class PowerMonitor:

        def __init__(self):
            super().__init__()
            self.normalThreshold = 7
            self.warningThreshold = 6.5
            self.cutOffThreshold = 6
            self.currentStatus = 0
            if distro_ID == "Raspbian":
                self.battery_status = { "POWEROFF":Color(255, 0, 0), # RED
                                        "WARNING":Color(240, 165, 0), # YELLOW
                                        "NORMAL":color(0, 255, 0)}   # GREEN
            else:
                self.battery_status = {"POWEROFF": "RED",  # RED
                                       "WARNING": "YELLOW",  # YELLOW
                                       "NORMAL": "GREEN"}  # GREEN
            self.notification_delay = 2

        def get_battery_infor(self):
            power = 0.0
            if distro_ID == "Raspbian":
                adc = ADS7830()
                for i in range(3):
                    power += adc.readAdc(0)/255.0*5.0*3
                    time.sleep(0.01)
                power = round(power/3, 2)
            else:
                power = float(input("Input some dummy code for testing: "))
            if power >= self.normalThreshold:
                self.currentStatus = self.battery_status["NORMAL"]
                print("Battery is in normal state")
            elif (power >= self.warningThreshold) and (power < self.normalThreshold):
                self.currentStatus = self.battery_status["WARNING"]
                print("Battery is in warning state")
            elif (power >= self.cutOffThreshold) and (power < self.warningThreshold):
                self.currentStatus = self.battery_status["POWEROFF"]
                print("Battery is in poweroff state")
            else:
                self.currentStatus = 0
                self.currentStatus = self.battery_status["POWEROFF"]
                print("Battery is in undefined state")

        def display_status_led(self):
            while True:
                self.get_battery_infor()
                if distro_ID == "Raspbian":
                    if self.currentStatus != 0:
                        led=Led()
                        led.colorWipe(led.strip, self.currentStatus)
                else:
                    print("LED status: ", self.currentStatus)
                time.sleep(power_monitor.notification_delay)


if __name__ == "__main__":
    power_monitor = PowerMonitor()
    t = threading.Thread(power_monitor.display_status_led())
    t.start()


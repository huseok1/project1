from pms7003 import Pms7003Sensor,PmsSensorException
import RPi.GPIO as GPIO
import time
sensor=Pms7003Sensor('/dev/ttyUSB0')
import RPi_I2C_driver
#sensor=Pms7003Sensor('/dev/ttyAMA1')
lcd=RPi_I2C_driver.lcd(0x27)


GPIO.setwarnings(False)

try:
    while 1:
        lcd.setCursor(0,0)
        Dust=sensor.read()
        print('PM10 :\t',Dust['pm10'])
        lcd.print("PM10 : {:.2f}\n".format (Dust['pm10']))
        lcd.print("PM2.5 : {:.2f}\n".format (Dust['pm2_5']))
        lcd.print("PM1.0 : {:.2f}\n".format (Dust['pm1_0']))
            

except PmsSensorException:
    print('Connection problem')
            
finally:
    GPIO.cleanup()
    sensor.close()
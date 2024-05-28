from pms7003 import Pms7003Sensor,PmsSensorException
import RPi.GPIO as GPIO
import time
import RPI_I2C_driver

sensor=Pms7003Sensor('/dev/ttyAMA1')
A1A_PIN=23
lcd=RPI_I2C_driver.lcd(0x27)#RPI_I2C_driver.lcd(I2C주소)


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(A1A_PIN,GPIO.OUT)

PWM_FREQ=50
A1A=GPIO.PWM(A1A_PIN,PWM_FREQ)

try:
    while 1:
        Dust=sensor.read()
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.print('PM10:\t{:.2f}'.format(Dust['pm10']))
        time.sleep(0.5)
        if Dust['pm10']>70:
            A1A.start(0)
            A1A.ChangeDutyCycle(70)
        elif Dust['pm10']<30:  
            A1A.stop()
        elif pressed==0:
            A1A.stop()
except PmsSensorException:
    print('Connection problem') 
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()


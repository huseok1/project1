import RPi.GPIO as GPIO
import time
import math

GPIO.setwarnings(False)

PWM_PIN1 = 12
PWM_PIN2 = 13

# 드라이브 모드 핀
DIR_PIN_1 = 5
DIR_PIN_2 = 6

DIR_PIN_3 = 7
DIR_PIN_4 = 8

# PWM 초기 설정
PWM_FREQUENCY1 = 1000  # Hz
PWM_FREQUENCY2 = 1000
INITIAL_DUTY_CYCLE1 = 0  # 듀티 사이클 초기 설정
INITIAL_DUTY_CYCLE2 = 0

sensor1_trigger = 20  # 앞 1
sensor1_echo = 21
sensor2_trigger = 22  # 오른쪽 1
sensor2_echo = 23
sensor3_trigger = 24  # 수정 필요
sensor3_echo = 25
sensor4_trigger = 26  # 서보로 작동하는  앞족 서보 2
sensor4_echo = 27


GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor1_trigger, GPIO.OUT)
GPIO.setup(sensor1_echo, GPIO.IN)
GPIO.setup(sensor2_trigger, GPIO.OUT)
GPIO.setup(sensor2_echo, GPIO.IN)
GPIO.setup(sensor3_trigger, GPIO.OUT)
GPIO.setup(sensor3_echo, GPIO.IN)
GPIO.setup(sensor4_trigger, GPIO.OUT)
GPIO.setup(sensor4_echo, GPIO.IN)

# 서보모터
servoPIN = 17  # 노란색핀
SERVO_MAX_DUTY = 12
SERVO_MIN_DUTY = 2
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
servo = GPIO.PWM(servoPIN, 50)
servo.start(0)

# PWM 출력 핀 설정, 출력함수 설정
GPIO.setup(PWM_PIN1, GPIO.OUT)
GPIO.setup(DIR_PIN_1, GPIO.OUT)
GPIO.setup(DIR_PIN_2, GPIO.OUT)
pwm1 = GPIO.PWM(PWM_PIN1, PWM_FREQUENCY1)
pwm1.start(INITIAL_DUTY_CYCLE1)

GPIO.setup(PWM_PIN2, GPIO.OUT)
GPIO.setup(DIR_PIN_3, GPIO.OUT)
GPIO.setup(DIR_PIN_4, GPIO.OUT)
pwm2 = GPIO.PWM(PWM_PIN2, PWM_FREQUENCY2)
pwm2.start(INITIAL_DUTY_CYCLE2)


def measure_distance(trigger_pin, echo_pin):  # 초음파 센서 함수
    time.sleep(0.1)
    GPIO.output(trigger_pin, True)
    time.sleep(0.00001)
    GPIO.output(trigger_pin, False)

    while GPIO.input(echo_pin) == 0:
        pulse_start = time.time()
    while GPIO.input(echo_pin) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17125  # Speed of sound is 343 m/s, or 17125 cm/s
    distance = round(distance, 2)

    return distance


def setServoPos(degree):
    degree = min(degree, 220)
    degree = max(degree, 0)
    duty = SERVO_MIN_DUTY + (degree * (SERVO_MAX_DUTY - SERVO_MIN_DUTY) / 220.0)
    servo.ChangeDutyCycle(duty)


def set_direction(direction):  # 방향 설정 함수
    if direction == "00":
        GPIO.output(DIR_PIN_1, GPIO.LOW)
        GPIO.output(DIR_PIN_2, GPIO.LOW)
    elif direction == "10":
        GPIO.output(DIR_PIN_1, GPIO.HIGH)  # 모터 드라이브 로직에 기반해 핀 모드 설정
        GPIO.output(DIR_PIN_2, GPIO.LOW)
        GPIO.output(DIR_PIN_3, GPIO.HIGH)
        GPIO.output(DIR_PIN_4, GPIO.LOW)
    elif direction == "01":
        GPIO.output(DIR_PIN_1, GPIO.LOW)
        GPIO.output(DIR_PIN_2, GPIO.HIGH)
        GPIO.output(DIR_PIN_3, GPIO.HIGH)
        GPIO.output(DIR_PIN_4, GPIO.LOW)
    elif direction == "11":
        GPIO.output(DIR_PIN_1, GPIO.HIGH)
        GPIO.output(DIR_PIN_2, GPIO.LOW)
        GPIO.output(DIR_PIN_3, GPIO.LOW)
        GPIO.output(DIR_PIN_4, GPIO.HIGH)



def side_angle(dis1,dis2):
    y = dis1 - dis2
    angle = math.atan2(y, 12) * 180.0 / math.pi  # 12 은 두 센서 사이의 거리
    print(angle,':오차각도')
    print(dis1,dis2,('오른쪽 거리 1,2'))
    angle = round(angle,2)
    return angle

#오른쪽에 있는 두 초음파센서의 거리차로 정방향 정렬 제어목적
def run(dis1,dis2):
    if dis1>dis2:
        while dis1-dis2 >= 2:
            setServoPos(85)
    elif dis2<dis1:
        while dis2-dis1 >= 2:
            setServoPos(105)
    
def turn(frontdis):
    setServoPos(65)
    if frontdis>40:
        setServoPos(95)
def turn2(frontdis):
    setServoPos(125)
    if frontdis>40:
        setServoPos(95)
#다음 공간에서 정렬하는 것 까지
def exit():

def main():
    try:
        #정방향 회전
        set_direction("10")
        #초기 방향설정
        setServoPos(95)
        #바퀴 회전 설정(약하게 하는 것이 제어가 쉬울듯함)
        pwm1.ChangeDutyCycle(60)
        pwm2.ChangeDutyCycle(60)
        while True:
            dis1=measure_distance(sensor1_trigger,sensor1_echo)
            dis2=measure_distance(sensor2_trigger,sensor2_echo)
            dis3=measure_distance(sensor3_trigger,sensor3_echo)
            dis4=measure_distance(sensor4_trigger,sensor4_echo)
            b=0
            #전방향 거리가 넉넉하면 일반 주행
            if dis3>40 & dis1<20:
                run(dis1,dis2)
            elif dis3<20:
                turn(dis3)
                b+=1
            while b>5:
                if dis1>40:
                    exit()
                    b=0


                
    except KeyboardInterrupt:
        pass
if __name__ =='__main__':
    main()
    GPIO.cleanup()
    pwm1.stop()
    pwm2.stop()
    servo.stop()

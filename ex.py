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



def side_angle():
    distance2 = measure_distance(sensor2_trigger, sensor2_echo)  # 사이드 두개의 초음파 센서 2가 앞 센서
    distance3 = measure_distance(sensor3_trigger, sensor3_echo)
    if(distance2-distance3)<5:
        distance2 = distance3 #탈출이랑 구별, 일반 주행 시 출구 조우 시 탈출할것 고려
    y = distance2 - distance3
    angle = math.atan2(y, 3) * 180.0 / math.pi  # 3 은 두 센서 사이의 거리
    print(angle,':오차각도')
    print(distance2,distance3,('오른쪽 거리 1,2'))
    angle=round(angle,2)
    return angle


def servo_direction():  # 운행용 함수
    distance1 = measure_distance(sensor1_trigger, sensor1_echo)
    distance2 = measure_distance(sensor2_trigger, sensor2_echo)  # 사이드 두개의 초음파 센서 2가 앞 센서
    distance3 = measure_distance(sensor3_trigger, sensor3_echo)
    distance4 = measure_distance(sensor4_trigger, sensor4_echo)
    y = distance2 - distance3

    watcher = side_angle()  # 진행방향 Y 축 기준으로 +-각도
    antiwat = - watcher

    # 정면 센서 인식값이 매우 높다면?? 방 이동중이거나 이상한 방향으로 가고있던가... 이상한 방향으로 이동중이면 오른쪽 센서에 값이 과도하게 높을것

    if distance1 > 30:  # 벽면을 인식하고 있을때 방향전환 여기는 일반적인 직선 주행 상황
        if y > 7:  # 오른쪽 벽과 과도하게 떨어져 있을때 오른쪽으로 이동 1차 방향 제어 필터

            setServoPos(125)
            time.sleep(1.5)
            setServoPos(95)  # 정면정렬
        elif y < -7:
            setServoPos(75)  # 기체가 오른쪽 벽면과 너무 멀거나 가까울때
            time.sleep(1)
            setServoPos(95)  # 정면정렬

        if watcher < 5:  # 현재 기체가 직선이 아닌  왼쪽으로 진행중, 서보모터가 오른쪽을 볼 필요가 있음
            while watcher == 0:
                setServoPos(95 + antiwat)  # 95은 초기 모터 영점 조절 필요 정면과 오차가 있는 각도 피드백값만큼 역방향으로 진행
            setServoPos(95)
        elif watcher > 5:
            while watcher == 0:  # 직선주행을 할 때까지 서보모터의 각도를 조정
                setServoPos(95 + antiwat)
            setServoPos(95)
    elif distance1 < 30:  # 정면 벽과 과도하게 가까워지기 시작, 방향 전환 필요
        if distance1 <= 3:  # 충돌 직전
            while distance1 >= 20:
                pwm1.ChangeDutyCycle(0)
                pwm2.ChangeDutyCycle(0)
                time.sleep(2)
                set_direction('01')  # 정지 후 후진
                pwm1.ChangeDutyCycle(50)
                pwm2.ChangeDutyCycle(50)
                time.sleep(4)
                set_direction('10')  # 전진설정
        while distance1 > 30:
            setServoPos(75)  # 일반적인 상황 방향전환
        setServoPos(95)



def aircondition():
    return 1


def exit():
    distance1 = measure_distance(sensor1_trigger, sensor2_echo)
    distance2 = measure_distance(sensor2_trigger, sensor2_echo)  # 사이드 두개의 초음파 센서 2가 앞 센서
    distance3 = measure_distance(sensor3_trigger, sensor3_echo)
    distance4 = measure_distance(sensor4_trigger, sensor4_echo)
    y = distance2 - distance3
    sum_dis23 = distance2 + distance3

    while ((sum_dis23)/ 2) > 20:  # 오른쪽이 뚫려있을때까지 운행 평균인 이유.. 한번에 뚤려있어 전방 센서 값이 튀는걸 완화
        servo_direction()
        if ((sum_dis23) / 2) > 20:
            while sum_dis23 < 15:
                setServoPos(125)
            print('exit complite')
            setServoPos(95)



try:
    # 운행 초기 설정
    set_direction("10")
    # 모터 회전 방향 설정, 출력 100 설정
    pwm1.ChangeDutyCycle(50)
    pwm2.ChangeDutyCycle(50)
    # 서보 모터 초기 위치
    setServoPos(95)
    while True:
        servo_direction()


except KeyboardInterrupt:  # 키보드 인터럽트로 함수 종료
    servo.stop()
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()
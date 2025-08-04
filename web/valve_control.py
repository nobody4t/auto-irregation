import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
shuifa_pin = 18

GPIO.setup(shuifa_pin, GPIO.OUT)
def control_watervalve(operate):
    if operate == "open":
        GPIO.output(shuifa_pin, GPIO.HIGH)
        print("水阀开启")
    elif operate == "close":
        GPIO.output(shuifa_pin, GPIO.LOW)
        print("水阀关闭")

if __name__=="__main__":
    control_watervalve("close")
    
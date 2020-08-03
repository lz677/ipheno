#! C:\Users\93715\Anaconda3\python.exe
# *-* coding:utf8 *-*
"""
@author: LiuZhe
@license: (C) Copyright SJTU ME
@contact: LiuZhe_54677@sjtu.edu.cn
@file: fan.py
@time: 2020/7/20 15:09
@desc: LESS IS MORE
"""
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges."
          + "You can achieve this by using 'sudo' to run your script")
import logging


class Fan(object):
    def __init__(self, pin: int = 29):
        # 默认pwn 引脚为29
        self.pin = pin
        self.mode = GPIO.BOARD
        self.pwm = None
        self.frequency = 25000
        self.duty = 0
        self.duty_max = 100
        self.initialization()

    # 修改引脚
    def set_light_pin(self, pin: int) -> bool:
        # self.clean_gpio()
        if (self.mode == GPIO.BOARD and 1 <= pin <= 40) or (self.mode == GPIO.BCM and 1 <= pin <= 27):
            self.pin = pin
            self.initialization()
            self.set_duty(self.duty)
            return True
        return False

    # 修改 GPIO引脚模式
    # TODO：测试未成功
    def set_mode(self, mode) -> bool:
        if self.mode in (GPIO.BOARD, GPIO.BCM):
            self.mode = mode
            GPIO.setmode(mode)
            return True
        return False

    # 初始化
    def initialization(self):
        GPIO.setmode(self.mode)
        GPIO.setup(self.pin, GPIO.OUT)
        # 默认关灯
        GPIO.output(self.pin, False)
        self.pwm = GPIO.PWM(self.pin, self.frequency)
        self.pwm.start(0)

    # 风扇开启
    def fan_open(self, duty: int = 10) -> bool:
        logging.debug('频率为%d' % self.frequency)
        if 0 <= duty <= self.duty_max:
            self.set_duty(duty)
            self.pwm.ChangeDutyCycle(duty)
            return True
        elif duty < 0:
            self.set_duty(0)
            self.pwm.ChangeDutyCycle(0)
        elif duty > self.duty_max:
            self.set_duty(self.duty_max)
            self.pwm.ChangeDutyCycle(self.duty_max)

    # 风扇关闭
    def fan_close(self):
        self.pwm.ChangeDutyCycle(0)

    # 修改频率
    def set_frequency(self, frequency):
        self.pwm.stop()
        self.frequency = frequency
        self.pwm = GPIO.PWM(self.pin, self.frequency)
        self.pwm.start(self.duty)

    # 修改 占空比
    def set_duty(self, duty):
        if 0 <= duty <= self.duty_max:
            self.duty = duty
            self.pwm.ChangeDutyCycle(self.duty)
        elif duty > self.duty_max:
            self.duty = self.duty_max
            self.pwm.ChangeDutyCycle(self.duty_max)
        else:
            self.duty = 0
            self.pwm.ChangeDutyCycle(self.duty)

    # 清楚引脚
    def clean_gpio(self):
        GPIO.cleanup(self.pin)


if __name__ == '__main__':
    import time

    try:
        fan1 = Fan()
        print("开始测试：")
        fan_fre = int(input("请输入频率(Hz): "))
        fan1.set_frequency(fan_fre)
        print("当前频率为：", fan1.frequency)
        print("1/5 风扇开启5s")
        if not fan1.fan_open(10):
            exit(-677)
        time.sleep(5)
        print("2/5 风扇变快5s")
        fan1.set_duty(30)
        time.sleep(5)
        print("3/5 风扇被关闭3s")
        fan1.fan_close()
        # fan_gpio = int(input("请输入修改的引脚(不为19): "))
        # fan1.set_light_pin(fan_gpio)
        # fan_fre = int(input("请输入频率(Hz): "))
        # fan1.set_frequency(fan_fre)
        # print("4/5 当前频率为：", fan1.frequency)
        # print("风扇开启5s")
        # if not fan1.fan_open(10):
        #     exit(-677)
        # time.sleep(5)
        # print("5/5 测试完毕")
    except KeyboardInterrupt:
        print("程序被外部中断")

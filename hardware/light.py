#! C:\Users\93715\Anaconda3\python.exe
# *-* coding:utf8 *-*
"""
@author: LiuZhe
@license: (C) Copyright SJTU ME
@contact: LiuZhe_54677@sjtu.edu.cn
@file: light.py
@time: 2020/7/20 13:59
@desc: LESS IS MORE
"""

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges."
          + "You can achieve this by using 'sudo' to run your script")


# 可以用于 灯和发光板
class Light(object):
    def __init__(self, pin: int):
        # 默认引脚
        self.pin = pin
        self.mode = GPIO.BOARD
        self.initialization()

    # 修改引脚
    def set_light_pin(self, pin: int) -> bool:

        if (self.mode == GPIO.BOARD and 1 <= pin <= 40) or (self.mode == GPIO.BCM and 1 <= pin <= 27):
            self.clean_gpio()
            self.pin = pin
            self.initialization()
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
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(19, GPIO.OUT, initial=True)
        # 默认关灯
        GPIO.output(self.pin, False)

    def clean_gpio(self):
        GPIO.cleanup(self.pin)

    # 开灯
    def light_on(self):
        GPIO.output(self.pin, True)

    # 关灯
    def light_off(self):
        GPIO.output(self.pin, False)


if __name__ == '__main__':
    import time

    try:
        light1 = Light(29)
        print("灯测试开始")
        print("1/3 灯亮5秒")
        light1.light_on()
        time.sleep(5)
        print('*' * 50)
        print("2/3 灯暗5秒")
        light1.light_off()
        time.sleep(5)
        print('*' * 50)
        # print("3/3 修改引脚")
        # gpio_change = int(input("请输入修改的引脚值[1,40]\n"))
        # light1.set_light_pin(gpio_change)
        # print("3.1/3.2 灯亮5秒")
        # light1.light_on()
        # time.sleep(5)
        # print('*' * 50)
        # print("3.2/3.2 灯暗5秒")
        # light1.light_off()
        # time.sleep(5)
        print("测试完成")
    except KeyboardInterrupt:
        print("程序被外部中断")

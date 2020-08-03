#! C:\Users\93715\Anaconda3\python.exe
# *-* coding:utf8 *-*
"""
@author: LiuZhe
@license: (C) Copyright SJTU ME
@contact: LiuZhe_54677@sjtu.edu.cn
@file: motor.py
@time: 2020/7/14 16:48
@desc: LESS IS MORE
"""
import time
import typing
# from trans_try import cancel
# from app_config.app_task import gl_motor_stop
from hardware import gl
import logging

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    print("motor depend on RPi.GPIO, so run it on RPi please")
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges."
          + "You can achieve this by using 'sudo' to run your script")


# 仅向外提供初始化、抬升、下降、打开、关闭接口
class Motor(object):
    def __init__(self, gpio_pins: typing.List[int], mode=GPIO.BOARD, frequency=800):
        self.mode = mode
        # GPIO.setmode(GPIO.BOARD)
        self.pins = gpio_pins  # 引脚列表
        self.COM = gpio_pins[0]  # COM 3.3-5v 采用共阳极
        self.DIR = gpio_pins[1]  # DIR direction 方向信号 0V Vcom
        self.STP = gpio_pins[2]  # STP 步进信号 100-20KHz
        self.EN = gpio_pins[3]  # 脱机信号 Vcom使能电机 0V步进电机脱机状态
        self.able_status = False  # 默认不使能
        self.direction_is_cw = True  # True 电机方向为顺时针 False为逆时针
        self.frequency = frequency
        self.duty = 0
        self.duty_max = 100
        self.pwm = None  # 初始化PWM实例 频率为100-20kHz 1600 -> 1r/s
        self.initialization()

    # 初始化驱动器的GPIO
    def initialization(self):
        """
        初始化驱动器的GPIO
        :return: None
        """
        GPIO.setmode(self.mode)
        GPIO.setup(self.pins, GPIO.OUT)
        # COM-True DIR-True STP-False EN-False
        GPIO.output(self.pins, (True, True, False, False))
        self.pwm = GPIO.PWM(self.STP, self.frequency)  # 初始化PWM实例 频率为100-20kHz 1600 -> 1r/s
        # 启动pwm
        self.pwm.start(0)
        self.direction_is_cw = True
        self.able_status = False

    # set numbering system BOARD or BCM
    def set_mode(self, mode) -> bool:
        """
        set numbering system：BOARD or BCM
        :param mode: GPIO.BOARD, GPIO.BCM
        :rtype: bool
        :return: True:设置成功 False:没有该模式
        """
        if mode in (GPIO.BOARD, GPIO.BCM):
            self.mode = mode
            GPIO.setmode(mode)
            return True
        return False

    # set the pwm
    def set_pwm_frequency(self, frequency: int) -> bool:
        """
        修改驱动器PWM的频率，可以改变速度，频率为100-20kHz 1600Hz -> 1r/s
        :param frequency: 频率 100-20kHz
        :return: 是否设置成功
        """
        if 100 < frequency < 20000:
            self.pwm.stop()
            self.frequency = frequency
            print("当前频率为： ", frequency)
            self.pwm = GPIO.PWM(self.STP, frequency)
            self.pwm.start(self.duty)
            return True
        return False

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

    # 使能电机
    def set_able_status(self, is_enable: bool = True):
        """
        修改电机的使能状态
        :param is_enable: 是否要使能
        :return: None
        """
        GPIO.output(self.EN, is_enable)
        self.able_status = is_enable

    # 改变电机转向
    def set_direction(self, is_cw: bool = True):
        """
        修改电机的旋转方向
        :param is_cw: 是否为顺时针旋转
        :return: None
        """
        GPIO.output(self.DIR, is_cw)
        self.direction_is_cw = is_cw

    # 修改 GPIO
    def set_pins(self, gpio_pins):
        self.pins = gpio_pins  # 引脚列表
        self.COM = gpio_pins[0]  # COM 3.3-5v 采用共阳极
        self.DIR = gpio_pins[1]  # DIR direction 方向信号 0V Vcom
        self.STP = gpio_pins[2]  # STP 步进信号 100-20KHz
        self.EN = gpio_pins[3]  # 脱机信号 Vcom使能电机 0V步进电机脱机状态
        self.initialization()

    # return which pin numbering system
    def which_mode(self):
        return GPIO.getmode()

    # get the pwm
    def get_pwm(self):
        return self.pwm

    # 清除电机引脚
    def clean_up(self):
        """
        清除电机使用的引脚
        :rtype: bool -> True清除引脚成功
        """
        try:
            GPIO.cleanup(self.pins)
            return True
        except KeyError:
            return False
        except RuntimeError:
            return False


class TravelSwitch(object):
    def __init__(self, pins, mode=GPIO.BOARD):
        self.mode = mode
        self.pins = pins
        self.pin_NC = pins[0]
        self.pins_NO = pins[1]
        self.initialization()

    def initialization(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pins, GPIO.IN)

    def get_switch_status(self) -> bool:
        """
        返回行程开关的状态, and的目的是 有任何问题（接触不良）都要保证安全。
        :return: True-> 行程开关触发
                 False->行程开关未触发
        """
        # logging.debug('no:' + str(GPIO.input(self.pins_NO)))
        # logging.debug('nc:' + str(GPIO.input(self.pin_NC)))
        # logging.debug('zong' + str(GPIO.input(self.pins_NO) and not GPIO.input(self.pin_NC)))
        return GPIO.input(self.pins_NO) and not GPIO.input(self.pin_NC)


class MotorAction(object):
    def __init__(self, motor_name, motor_pins, switch_pins, frequency):
        self.name = motor_name
        self.motor = Motor(motor_pins, frequency=frequency)
        self.begin_switch = TravelSwitch(switch_pins[0:2])
        self.end_switch = TravelSwitch(switch_pins[-2:])

    # 初始位置或终止位置
    def goto_position(self, is_goto_begin: bool, duty) -> bool:
        self.motor.set_able_status(True)
        self.motor.set_direction(is_goto_begin)
        # self.motor.set_pwm_frequency(frequency)
        begin_time = time.time()
        if (is_goto_begin and not self.begin_switch.get_switch_status()) or (
                not is_goto_begin and not self.end_switch.get_switch_status()):
            self.motor.set_duty(duty)
            while True:
                if gl['gl_motor_stop']:
                    logging.debug('gl_motor_stop')
                    break
                elif self.begin_switch.get_switch_status() and is_goto_begin:
                    logging.debug('self.begin_switch.get_switch_status()')
                    break
                elif self.end_switch.get_switch_status() and not is_goto_begin:
                    logging.debug('end_switch.get_switch_status()')
                    break
                elif time.time() - begin_time > 30:
                    logging.debug('time30')
                    break
                time.sleep(0.001)
        self.motor.set_able_status(False)
        self.motor.pwm.ChangeDutyCycle(0)
        if self.begin_switch.get_switch_status() or self.end_switch.get_switch_status():
            return True
        return False

    # 初始化到初始位置
    def initialization(self, frequency, duty) -> bool:
        print("正在初始化 %s......" % self.name)
        # 一开始就处于初始化的状态
        if self.begin_switch.get_switch_status():
            time.sleep(0.5)
            if self.begin_switch.get_switch_status():
                self.motor.set_able_status(False)
                print("%s 初始化完毕" % self.name)
                return True
            else:
                if self.goto_position(True, duty):
                    print("\n%s 初始化完成" % self.name)
                    return True
        else:
            if self.goto_position(True, duty):
                print("\n%s 初始化完成" % self.name)
                return True
        return False

    # 关闭或者开启
    def action(self, is_goto_begin: bool, duty) -> bool:
        if is_goto_begin:
            print("正在回到初始位置...")
            res = self.goto_position(True, duty)
            if res:
                print("已经回到初始位置")
                return True
            return False
        else:
            print("正在抵达终止位置...")
            res = self.goto_position(False, duty)
            if res:
                print("已经抵达终止位置")
                return True
            return False


# 功能测试代码 用一个电机
def test_step1():
    # 测试上述代码是否好用
    # drawer = Motor([32, 36, 38, 40], frequency=4000)
    # drawer.initialization()
    lifting = Motor([31, 33, 35, 37], frequency=800)
    # 修改模式
    print("修改模式测试...")
    # lifting.set_mode(GPIO.BCM)
    # if lifting.which_mode() != GPIO.BCM:
    #     print("set_mode或which_mode有问题")
    #     exit(-100)
    lifting.set_mode(GPIO.BOARD)
    if lifting.which_mode() != GPIO.BOARD:
        print("set_mode或which_mode有问题")
        exit(-100)
    # 使能测试:
    print("使能测试...")
    lifting.set_able_status(True)
    lifting.get_pwm().ChangeDutyCycle(10)
    print("此时应该有力 10s")
    time.sleep(10)
    print("反转方向: 10s")
    lifting.set_direction(False)
    time.sleep(10)
    print("速度变快：10s")
    if lifting.set_pwm_frequency(1600):
        lifting.get_pwm().ChangeDutyCycle(10)
    time.sleep(10)
    print("停转")
    lifting.set_able_status(False)
    print("此时应该没力 30s")
    time.sleep(10)
    lifting.clean_up()
    print("测试结束")


# 逻辑测试代码 用一个开关电源测试
def test_step2():
    drawer = MotorAction('托盘', [31, 33, 35, 37], [12, 16, 18, 22], frequency=4000)
    lifting = MotorAction('抬升', [32, 36, 38, 40], [13, 15, 7, 11], frequency=800)
    # drawer = MotorAction('托盘', [32, 36, 38, 40], [7, 11, 7, 11])
    # lifting = MotorAction('抬升', [31, 33, 35, 37], [7, 11, 7, 11])
    print("初始化抽屉 等待3s")
    time.sleep(3)
    drawer.initialization(4000, 5)

    print()
    print("初始化抬升 等待3s")
    time.sleep(3)
    lifting.initialization(800, 10)
    print("初试化结束")

    print('*' * 50)
    print("抽屉测试开始 等待3s")
    time.sleep(3)
    drawer.action(False, 5)

    print()
    time.sleep(3)
    drawer.action(True, 5)
    print("抽屉测试结束")

    print('*' * 50)
    print("抬升测试开始 等待3s")
    time.sleep(3)
    lifting.action(False, 10)

    print()
    time.sleep(3)
    lifting.action(True, 10)
    print("抬升测试结束")

    print('*' * 50)
    drawer.motor.clean_up()
    lifting.motor.clean_up()
    print('测试结束')


if __name__ == '__main__':
    try:
        pass
        # test_step2()
        # print(cancel)
    except KeyboardInterrupt:
        print("程序中断")

#! C:\Users\93715\Anaconda3\python.exe
# *-* coding:utf8 *-*
"""
@author: LiuZhe
@license: (C) Copyright SJTU ME
@contact: LiuZhe_54677@sjtu.edu.cn
@file: step_motor_encoder.py
@time: 2020/7/16 19:54
@desc: LESS IS MORE
"""
import time

try:
    from smbus2 import SMBus
except ModuleNotFoundError:
    print("please run it on RPi")
except RuntimeError:
    print("pleas install sumbus")


class Encoder(object):
    def __init__(self):
        self.slave_addr = 0x36
        self.circle = 0
        self.start_angle = 95

    # 修改从机地址
    def set_slave_addr(self, slave_addr):
        self.slave_addr = slave_addr

    # 设定初试角度
    def set_start_angle(self, start_angle: float):
        self.start_angle = start_angle

    def get_start_angle(self) -> float:
        return self.start_angle

    # 读取Raw_angle 原始角度
    def get_raw_angle(self) -> float:
        # 原始角度寄存器内存储有未缩放的和未修改的角度值
        # 0x0C    RAW ANGLE   R       RAW ANGLE(11: 8)
        # 0x0D    RAW ANGLE   R    ANGLE(7: 0)
        # 360 <-> 4096
        with SMBus(1) as i2c_bus:
            # 读取的数据均为10进制
            low_8bits = i2c_bus.read_byte_data(self.slave_addr, 0x0D)
            high_4bits = i2c_bus.read_byte_data(self.slave_addr, 0x0C)
            # 求绝对编码值
            raw_code_value = (high_4bits << 8) + low_8bits
            # 求绝对角度
            raw_angle = raw_code_value / 4096 * 360
        return raw_angle

    # 读取angle 修整范围后的角度
    def get_angle(self) -> float:
        # 经过缩放的角度值可在角度寄存器中得到
        with SMBus(1) as i2c_bus:
            # 读取的数据均为10进制
            low_8bits = i2c_bus.read_byte_data(self.slave_addr, 0x0F)
            high_4bits = i2c_bus.read_byte_data(self.slave_addr, 0x0E)
            # 求绝对编码值
            code_value = (high_4bits << 8) + low_8bits
            # 求绝对角度
            angle = code_value / 4096 * 360
        return angle

    # 电机的绝对角度 可能大于360
    def get_absolute_angle(self, circle) -> float:
        return self.get_angle() + 360 * circle - self.start_angle

    # 角度设置，角度范围
    def set_angle(self):
        pass

    # 改变方向
    # AS5600可以通过DIR引脚控制磁场的旋转方向。如果DIR连接 到GND(DIR=0) ，从顶部观察到的顺时针旋转会增加角度值。
    # 如果DIR引脚连接到VDD(DIR=1) 逆时针旋转磁场将会使得角度值增大
    def inverse_direction(self):
        # 改变对应GPIO的拉高拉低
        pass


if __name__ == '__main__':
    ec = Encoder()
    ec.set_start_angle(95)
    angle_test, last_angle, cir = ec.get_start_angle(), ec.get_start_angle(), 0
    t = 1
    try:
        print("测试开始")
        while True:
            angle_test = ec.get_angle()
            if (last_angle - angle_test) / t > 180:
                cir += 1
            elif (last_angle - angle_test) / t < - 180:
                cir -= 1
            last_angle = angle_test
            absolute_angle = ec.get_absolute_angle(cir)
            print("角度：", angle_test)
            print("圈数: ", cir)
            print("总角度:", absolute_angle)
            time.sleep(1)
    except KeyboardInterrupt:
        print("程序中断")

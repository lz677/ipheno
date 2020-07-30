#! C:\Users\93715\Anaconda3\python.exe
# *-* coding:utf8 *-*
"""
@author: LiuZhe
@license: (C) Copyright SJTU ME
@contact: LiuZhe_54677@sjtu.edu.cn
@file: uart.py
@time: 2020/7/15 21:08
@desc: LESS IS MORE
"""
import serial
import time


class Uart(object):
    def __init__(self, device_tty, bps=115200):
        self.device_tty = device_tty
        self.bps = bps

    def send_message(self, message: bytes):
        ser = serial.Serial(self.device_tty, self.bps)
        # 若串口未打开则打开串口
        if not ser.isOpen:
            ser.open()
        ser.write(message)  # 发送数据
        ser.close()  # 关闭串口

    # def receive_message(self) -> bytes:
    #     ser = serial.Serial(self.device, self.bps)
    #     if not ser.isOpen:
    #         ser.open()
    #     # 获得接收缓冲区字符
    #     count = ser.inWaiting()
    #     if count:
    #         # 读取内容
    #         recv = ser.read(count)
    #         # 清空接受缓存区
    #         ser.flushInput()
    #         ser.close()
    #         # 返回读取内容
    #         return recv
    #     ser.close()
    #     return b'Do not receive any data'

    def send_and_receive(self, message: bytes, timeout: float = 1.0, one_time: bool = True) -> bytes:
        ser = serial.Serial(self.device_tty, self.bps, timeout=timeout)
        if not ser.isOpen:
            ser.open()
        ser.write(message)  # 发送数据
        # time.sleep(0.1)
        ser.flushInput()
        count_timeout = 1
        while True:
            # TODO：出现问题 丢包接受不到信息，那么无返回数据，则接受处于死循环中。 初步用计数器解决
            # 获得接收缓冲区字符
            count_timeout += 1
            if one_time:
                if count_timeout % 500000 == 0:
                    break
            else:
                if count_timeout % 20000 == 0:
                    # print('进入循环了')
                    ser.write(message)  # 发送数据
                    # time.sleep(0.1)
                    ser.flushInput()
                    count_timeout = 1
            count = ser.inWaiting()
            if count:
                # 读取内容
                recv = ser.read(count)
                # 清空接受缓存区
                ser.flushInput()
                ser.close()
                # 返回读取内容
                return recv
            time.sleep(0.01)
        ser.close()
        return b'Do not receive any data'

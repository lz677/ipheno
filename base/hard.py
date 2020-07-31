#!/usr/bin/env python
# encoding: utf-8

"""
@version: Python3.7
@author: Zhiyu YANG, Liu Zhe
@e-mail: zhiyu_yang@sjtu.edu.cn, LiuZhe_54677@sjtu.edu.cn
@file: hard.py
@time: 2020/5/5 14:49

Code is far away from bugs with the god animal protecting
"""
from hardware import Capture
from base import __VERSION__
from typing import NewType

HardwareStatesType = NewType('HardwareStatesType', str)


class HardwareStates:
    camera = HardwareStatesType('camera')
    balance = HardwareStatesType('balance')
    printer = HardwareStatesType('printer')
    light_plate = HardwareStatesType('light_plate')
    light = HardwareStatesType('light')
    fan = HardwareStatesType('fan')
    plate_out = HardwareStatesType('plate_in')
    plate_down = HardwareStatesType('lifting')
    main = HardwareStatesType('main')


class Hardware:
    def __init__(self):
        """
        TODO：目前中间状态交给前端
        The status of hardware
        camera : '未连接' '已连接' '故障'
        balance: '未连接' '重量'
        printer: '未连接' '已连接' '打印中'
        light :   True  False'故障'
        fan :     True  False '故障'
        plate:    True  False
        main：     '运行中'
        """
        # initial status of hardware for reset
        self.init_states = {
            HardwareStates.camera: '未连接',
            HardwareStates.balance: '10000',
            HardwareStates.printer: '未连接',
            HardwareStates.light: False,
            HardwareStates.light_plate: False,
            HardwareStates.fan: False,
            HardwareStates.plate_out: False,
            HardwareStates.plate_down: False,
            HardwareStates.main: '运行中'
        }

        # hardware status
        self.all_states = {
            HardwareStates.camera: '未连接',  # 相机
            HardwareStates.balance: '- 6.77 g',  # 电子秤
            HardwareStates.printer: '未连接',  # 打印机
            HardwareStates.light: False,  # 灯
            HardwareStates.light_plate: False,  # 冷光片
            HardwareStates.fan: 0,  # 风扇
            HardwareStates.plate_out: False,  # 托盘 进出
            HardwareStates.plate_down: False,  # 托盘 上下
            HardwareStates.main: '运行中'  # 主控
        }

        # system information RPi
        self.system_info = {
            'version': __VERSION__,
            'staticIP': {
                'ip': '192.168.1.7',
                'port': '5000'
            },
            'temIP': {
                'ip': '192.168.1.7',
                'port': '5000'
            }
        }

        # error
        self.error_info = {
            HardwareStates.camera: 'Normal',
            HardwareStates.balance: 'Normal',
            HardwareStates.printer: 'Normal',
            HardwareStates.light: 'Normal',
            HardwareStates.light_plate: 'Normal',
            HardwareStates.fan: 'Normal',
            HardwareStates.plate_out: 'Normal',
            HardwareStates.plate_down: 'Normal',
            HardwareStates.main: 'Normal'
        }

        self.capture = Capture()

    def get_system_info(self):
        return self.system_info.copy()

    def get_all_states(self) -> dict:
        self.all_states[HardwareStates.camera] = '已连接' if self.capture.is_opened() else '未连接'
        return self.all_states.copy()

    def get_init_states(self) -> dict:
        self.init_states[HardwareStates.camera] = '已连接' if self.capture.is_opened() else '未连接'
        return self.init_states.copy()

    def get_error_info(self):
        return self.error_info.copy()

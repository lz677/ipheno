#! C:\Users\93715\Anaconda3\python.exe
# *-* coding:utf8 *-*
"""
@author: LiuZhe
@license: (C) Copyright SJTU ME
@contact: LiuZhe_54677@sjtu.edu.cn
@file: __init__.py.py
@time: 2020/7/28 11:31
@desc: LESS IS MORE
"""
from .capture import CaptureWebCam as Capture

gl = {
    'gl_motor_stop': False,
    'gl_weight_stop': False
}
WORK_ON_RPI = True
if WORK_ON_RPI:
    from .motor import Motor, TravelSwitch, MotorAction
    from .uart import Uart
    from .weight_sensor import WeightSensor
    from .step_motor_encoder import Encoder
    from .light import Light
    from .fan import Fan
    from .printer import Printer

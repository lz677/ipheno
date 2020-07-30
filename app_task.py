#! C:\Users\93715\Anaconda3\python.exe
# *-* coding:utf8 *-*
"""
@author: LiuZhe
@license: (C) Copyright SJTU ME
@contact: LiuZhe_54677@sjtu.edu.cn
@file: app_task.py
@time: 2020/7/29 9:01
@desc: LESS IS MORE
"""
# 官方库
import time
import cv2 as cv

# 开发库 # 注意导入顺序的影响
from base import Hardware, HardwareStates, utility
from base import Results
from hardware import WORK_ON_RPI
from typing import List, Tuple, NewType
from app_conf import ActionBase, logger, States, Task

ActionNameType = NewType('ActionNameType', str)
TaskNameType = NewType('TaskNameType', str)
# 树莓派跑 or 自机测试
if WORK_ON_RPI:
    from hardware import MotorAction, WeightSensor, Light, Fan, Printer

    gl_motor_stop: bool = False
    gl_weight_stop: bool = False

# TODO: 完成后删除测试库
import random

# 类实例化
hardware_info = Hardware()
results_info = Results()
if WORK_ON_RPI:
    drawer_hard = MotorAction('托盘', [31, 33, 35, 37], [12, 16, 18, 22], 8000)
    lifting_hard = MotorAction('抬升', [32, 36, 38, 40], [13, 15, 7, 11], 3200)
    weight_hard = WeightSensor('/dev/ttyAMA0')
    light_hard = Light(29)
    light_plate_hard = Light(23)
    fan_hard = Fan(19)
    printer_hard = Printer("COM7")


class ActionName:
    PLATE_IN = ActionNameType('托盘收回')
    PLATE_OUT = ActionNameType('托盘弹出')
    PLATE_UP = ActionNameType('托盘复位')
    PLATE_DOWN = ActionNameType('托盘下降')
    WEIGHT = ActionNameType('称重')
    LIGHT_ON = ActionNameType('打开顶灯')
    LIGHT_OFF = ActionNameType('关闭顶灯')
    PLATE_LIGHT_ON = ActionNameType('开冷光片')
    PLATE_LIGHT_OFF = ActionNameType('关冷光片')
    FAN = ActionNameType('风选机开')
    SET_IP_PORT = ActionNameType('设置静态IP和端口(PORT)')
    UPDATE_PRINTER_STATE = ActionNameType("查询打印机状态")
    PRINTER_PRINT = ActionNameType("打印数据")
    PRINTER_RESTART = ActionNameType('打印机重启')
    GRAIN_ANALYSIS = ActionNameType('谷粒分析')
    PANICLE_ANALYSIS = ActionNameType('穗形分析')
    COUNT_ANALYSIS = ActionNameType('穗上谷粒分析')
    GET_IMG = ActionNameType('获取图像(拍照)')


class TaskName:
    WEIGHT = TaskNameType('weight')
    WEIGHT_ZERO = TaskNameType('weight-zero')
    PLATE_OPEN = TaskNameType('plate-open')
    PLATE_CLOSE = TaskNameType('plate-close')
    LIGHT_ON = TaskNameType('light-on')
    LIGHT_OFF = TaskNameType('light-off')
    PLATE_LIGHT_ON = TaskNameType('plate-light-on')
    PLATE_LIGHT_OFF = TaskNameType('plate-light-off')
    FAN = TaskNameType('fan')
    SET_IP_PORT = TaskNameType('set-ip-port')
    UPDATE_PRINTER_STATE = TaskNameType('printer-state')
    PRINTER_PRINT = TaskNameType('printer-print')
    PRINTER_RESTART = TaskNameType('printer-restart')
    EASY_MODE = TaskNameType('easy-mode')


# 通用动作测试代码 给前端
def app_web_test(action):
    a = random.randint(1, 20)
    logger.debug('产生色随机数为: %d' % a)
    if a < 15:
        logger.debug('正在<%s>,等待3s' % action.name)
        # 以下代码被替代
        num = 1
        while num < 4:
            time.sleep(1)
            print('num:', num)
            num += 1
            if action.check_will_terminate():
                return False
        # 修改对应状态
        if action.name in (ActionName.PLATE_DOWN, ActionName.PLATE_UP):
            hardware_info.all_states[HardwareStates.plate_out] = (action.name == ActionName.PLATE_OUT)
        if action.name in (ActionName.PLATE_IN, ActionName.PLATE_OUT):
            hardware_info.all_states[HardwareStates.plate_down] = (action.name == ActionName.PLATE_DOWN)
        if action.name == ActionName.WEIGHT:
            hardware_info.all_states[HardwareStates.balance] = '6.66666'
        if action.name == ActionName.LIGHT_ON:
            hardware_info.all_states[HardwareStates.light] = True
        if action.name == ActionName.LIGHT_OFF:
            hardware_info.all_states[HardwareStates.light] = False
        if action.name == ActionName.PLATE_LIGHT_ON:
            hardware_info.all_states[HardwareStates.light_plate] = True
        if action.name == ActionName.PLATE_LIGHT_OFF:
            hardware_info.all_states[HardwareStates.light_plate] = False
        if action.name == ActionName.FAN:
            logger.info('--- 风扇打开,开度为%d' % hardware_info.all_states[HardwareStates.fan])
        if action.name == ActionName.SET_IP_PORT:
            # 判断ip 判断端口
            ip = hardware_info.system_info['temIP']['ip']
            port = hardware_info.system_info['temIP']['ip']
            if ip is not None or port is not None:
                if not utility.is_ipv4(ip):
                    action.states_resp.set_states(States.TERMINATE, _error_desc='ip地址不合法，请重新尝试')
                    logger.error('--- 动作"%s"被中止，由于ip地址不合法' % action.name)
                if not utility.is_port(port):
                    action.states_resp.set_states(States.TERMINATE, _error_desc='端口不合法，请重新尝试')
                    logger.error('--- 动作"%s"被中止，由于端口不合法' % action.name)
            hardware_info.system_info["staticIP"]["ip"] = ip
            hardware_info.system_info["staticIP"]["port"] = port
            utility.save_info_to_json(hardware_info, './doc/conf/main_control.json')

        action.states_resp.set_states(States.COMPLETE)
        logger.info('--- 动作"%s"完成' % action.name)
        return True
    else:
        action.states_resp.states = States.TERMINATE
        action.states_resp.set_states(States.TERMINATE, _error_desc=('未完全<%s>，请核查后再次启动' % action.name))
        logger.info('--- 动作"%s"未完成，错误原因：%s' % (action.name, action.states_resp.get_dict()['errorDesc']))


# 托盘复位
def plate_reset(action):
    if WORK_ON_RPI:
        if drawer_hard.goto_position(True, 10):
            hardware_info.all_states[HardwareStates.plate_out] = False
            if lifting_hard.goto_position(True, 10):
                hardware_info.all_states[HardwareStates.plate_down] = False
        else:
            action.states_resp.set_states(States.ERROR, _error_desc='托盘不能正常收回到最里侧')
            logger.error('--- 动作"%s"被中止，由于托盘不能正常收回到最里侧' % action.name)
    else:
        if random.randint(1, 20) < 15:
            logger.debug('--- 动作"%s"被中止，抽屉正在复位 等2s' % action.name)
            time.sleep(2)
            hardware_info.all_states[HardwareStates.plate_out] = False
            hardware_info.all_states[HardwareStates.plate_down] = False
            logger.debug('--- 抽屉复位完成')
        else:
            action.states_resp.set_states(States.ERROR, _error_desc='托盘不能正常收回到最里侧')
            logger.error('--- 动作"%s"被中止，由于托盘不能正常收回到最里侧' % action.name)


# 进料的出入
class PlateAction(ActionBase):
    def terminate(self):
        with self.lock:
            global gl_motor_stop
            gl_motor_stop = True
            self.will_terminate = True

    def run(self, task_name) -> bool:
        logger.info('--- 检查动作"%s"状态...' % self.name)
        time.sleep(0.1)

        for i in range(2):
            if self.check_will_terminate():
                self.states_resp.set_states(States.TERMINATE, _error_desc='被中止')
                logger.info('--- 动作"%s"被中止' % self.name)
                # TODO: 复位一下
                plate_reset(self)
                return False
            time.sleep(0.1)
        if WORK_ON_RPI:
            global gl_motor_stop
            gl_motor_stop = False
            # 电机在最高位置 然后满足两端条件
            if self.name in (ActionName.PLATE_IN, ActionName.PLATE_OUT) and lifting_hard.goto_position(True, 10) and \
                    drawer_hard.goto_position(self.name == ActionName.PLATE_IN, 10):
                # 修改信息及动作状态
                hardware_info.all_states[HardwareStates.plate_out] = (self.name == ActionName.PLATE_OUT)
                self.states_resp.set_states(States.COMPLETE)
                logger.info('--- 动作"%s"完成' % self.name)
                return True
            elif self.name in (ActionName.PLATE_UP, ActionName.PLATE_DOWN) and drawer_hard.goto_position(True, 10) and \
                    lifting_hard.goto_position(self.name == ActionName.PLATE_UP, 10):
                hardware_info.all_states[HardwareStates.plate_down] = (self.name == ActionName.PLATE_DOWN)
                self.states_resp.set_states(States.COMPLETE)
                logger.info('--- 动作"%s"完成' % self.name)
                return True
            else:
                # 如果有异常 宕掉电机 终止动作 反馈错误 并向前端提交具体错误信息供自修复
                gl_motor_stop = True
                self.states_resp.states = States.TERMINATE
                self.states_resp.set_states(States.TERMINATE, _error_desc=('<%s>未到位置，请核查后再次启动' % self.name))
                logger.warning('--- 动作"%s"未完成，错误原因：%s' % (self.name, self.states_resp.get_dict()['errorDesc']))
        else:
            app_web_test(self)
        return False


# 称重
class WeightAction(ActionBase):

    def terminate(self):
        with self.lock:
            global gl_weight_stop
            gl_weight_stop = True
            self.will_terminate = True

    def run(self, task_name) -> bool:
        logger.info('--- 检查动作"%s"状态...' % self.name)
        time.sleep(0.1)
        for i in range(2):
            if self.check_will_terminate():
                self.states_resp.set_states(States.TERMINATE, _error_desc='被中止')
                logger.info('--- 动作"%s"被中止' % self.name)
                # TODO: 复位一下
                plate_reset(self)
                hardware_info.all_states[HardwareStates.balance] = '- 6.77 g'
                return False
            time.sleep(0.1)
        if WORK_ON_RPI:
            global gl_weight_stop
            gl_weight_stop = False
            if task_name == TaskName.WEIGHT:
                # 称重
                weight_mean, weight_std = weight_hard.get_weight(3)
                # 修改结果信息
                hardware_info.all_states[HardwareStates.balance] = str(weight_mean) + ' +- ' + str(weight_std)
                logger.info('称重结果：' + str(weight_mean) + ' +- ' + str(weight_std))
            elif task_name == TaskName.WEIGHT_ZERO:
                # 清零
                if weight_hard.zero_weight():
                    hardware_info.all_states[HardwareStates.balance] = weight_hard.get_one_weight()
                    logger.info('称重清零完成,清零后的结果:' + str(hardware_info.all_states[HardwareStates.balance]))
                else:
                    # 如果有异常返回 异常
                    gl_weight_stop = True
                    self.states_resp.states = States.TERMINATE
                    self.states_resp.set_states(States.TERMINATE, _error_desc=('清零出现异常，请尝试再次启动' % self.name))
                    logger.warning('--- 动作"%s"未完成，错误原因：%s' % (self.name, self.states_resp.get_dict()['errorDesc']))
            # 状态变为完成
            self.states_resp.set_states(States.COMPLETE)
            logger.info('--- 动作"%s"完成' % self.name)
        else:
            app_web_test(self)
        return False


# 开关灯
class LightAction(ActionBase):
    def run(self, task_name) -> bool:
        # for i in range(2):
        #     if self.check_will_terminate():
        #         self.states_resp.set_states(States.TERMINATE, _error_desc='被中止')
        #         logger.info('--- 动作"%s"被中止' % self.name)
        #         # TODO: 复位一下
        #
        #         # plate_reset(self)
        #         # hardware_info.all_states[HardwareStates.balance] = '- 6.77 g'
        #         return False
        #     time.sleep(0.1)
        if WORK_ON_RPI:
            if task_name == TaskName.LIGHT_ON:
                # 开顶灯
                light_hard.light_on()
                # 修改结果信息
                hardware_info.all_states[HardwareStates.light] = True
                logger.info('--- 顶灯打开')
            elif task_name == TaskName.LIGHT_OFF:
                # 关顶灯
                light_hard.light_off()
                # 修改结果信息
                hardware_info.all_states[HardwareStates.light] = False
                logger.info('--- 顶灯关闭')
            elif task_name in (TaskName.PLATE_LIGHT_ON, TaskName.EASY_MODE):
                # 开冷光片
                light_plate_hard.light_on()
                # 修改结果信息
                hardware_info.all_states[HardwareStates.light_plate] = True
                logger.info('--- 冷光片打开')
            elif task_name in (TaskName.PLATE_LIGHT_OFF, TaskName.EASY_MODE):
                light_plate_hard.light_off()
                hardware_info.all_states[HardwareStates.light_plate] = False
                logger.info('--- 冷光片关闭')
            # elif
            # 状态变为完成
            self.states_resp.set_states(States.COMPLETE)
            logger.info('--- 动作"%s"完成' % self.name)
        else:
            app_web_test(self)
        return False


# 风扇
class FanAction(ActionBase):
    def run(self, task_name):
        if WORK_ON_RPI:
            # 开风扇
            fan_hard.fan_open(hardware_info.all_states[HardwareStates.fan])
            logger.info('--- 风扇打开,开度为%d' % hardware_info.all_states[HardwareStates.fan])
            # 状态变为完成
            self.states_resp.set_states(States.COMPLETE)
            logger.info('--- 动作"%s"完成' % self.name)
        else:
            app_web_test(self)
        return False


# 设置静态ip和端口
class SetIPAndPortAction(ActionBase):
    def run(self, task_name):
        if WORK_ON_RPI:
            # 判断ip 判断端口
            ip = hardware_info.system_info['temIP']['ip']
            port = hardware_info.system_info['temIP']['ip']
            if ip is not None or port is not None:
                if not utility.is_ipv4(ip):
                    self.states_resp.set_states(States.TERMINATE, _error_desc='ip地址不合法，请重新尝试')
                    logger.error('--- 动作"%s"被中止，由于ip地址不合法' % self.name)
                if not utility.is_port(port):
                    self.states_resp.set_states(States.TERMINATE, _error_desc='端口不合法，请重新尝试')
                    logger.error('--- 动作"%s"被中止，由于端口不合法' % self.name)
            hardware_info.system_info["staticIP"]["ip"] = ip
            hardware_info.system_info["staticIP"]["port"] = port
            utility.save_info_to_json(hardware_info, './doc/conf/main_control.json')
            utility.network_setup(ip, '255.255.255.0', '192.168.0.255')
            time.sleep(1)
            # 状态变为完成
            self.states_resp.set_states(States.COMPLETE)
            logger.info('--- 动作"%s"完成' % self.name)
        else:
            app_web_test(self)
        return False


# 打印机
class PrinterAction(ActionBase):
    def run(self, task_name):
        if WORK_ON_RPI:
            if task_name == TaskName.UPDATE_PRINTER_STATE:
                # TODO：修改打印机返回值 返回信息设置为错误信息
                if not printer_hard.printer_states():
                    self.states_resp.states = States.TERMINATE
                    self.states_resp.set_states(States.TERMINATE, _error_desc='打印机处于错误状态，请排除错误后再次测试')
                    logger.error('打印机处于错误状态，请排除错误后再次测试')
            elif task_name == TaskName.PRINTER_RESTART:
                printer_hard.printer_restart()
                logger.info('打印机重启')
            elif task_name == TaskName.PRINTER_PRINT:
                print_mes = {"品种号": '五优稻2号', '时间': str(time.time())}
                for para, result in enumerate(results_info.img_parameters):
                    if result != 'NONE':
                        print_mes.update({para: result})
                printer_hard.printer_print(print_mes, False)
            # 状态变为完成
            self.states_resp.set_states(States.COMPLETE)
            logger.info('--- 动作"%s"完成' % self.name)
        else:
            app_web_test(self)


# 拍照
class GetImgAction(ActionBase):
    def run(self, task_name):
        try:
            if not hardware_info.capture.is_opened():
                hardware_info.capture.open()
            hardware_info.capture.start_stream()
            # TODO: 路径问题核对
            cv.imwrite('algorithm/dlcount/img/easy_mode.png', hardware_info.capture.get_img())
        except IOError as io:
            self.states_resp.states = States.TERMINATE
            self.states_resp.set_states(States.TERMINATE, _error_desc='文件存储故障' + io)
            logger.error('--- 文件存储故障 <%s> ，请核查后重启任务' % io)
        except:
            self.states_resp.states = States.TERMINATE
            self.states_resp.set_states(States.TERMINATE, _error_desc='相机故障，请核查后重启任务')
            logger.error('--- 相机故障，请核查后重启任务')
        self.states_resp.set_states(States.COMPLETE)
        logger.info('--- 动作"%s"完成' % self.name)


# 调用count 算法
class CountAction(ActionBase):
    def run(self, task_name):
        pass


class TaskManager:
    plate_in_action = PlateAction(_name=ActionName.PLATE_IN)
    plate_out_action = PlateAction(_name=ActionName.PLATE_OUT)
    plate_down_action = PlateAction(_name=ActionName.PLATE_DOWN)
    plate_up_action = PlateAction(_name=ActionName.PLATE_UP)
    weight_action = WeightAction(_name=ActionName.WEIGHT)
    light_on_action = LightAction(_name=ActionName.LIGHT_ON)
    light_off_action = LightAction(_name=ActionName.LIGHT_OFF)
    fan_action = FanAction(_name=ActionName.FAN)
    ip_port_action = FanAction(_name=ActionName.SET_IP_PORT)
    printer_restart_action = PrinterAction(_name=ActionName.PRINTER_RESTART)
    printer_state_action = PrinterAction(_name=ActionName.UPDATE_PRINTER_STATE)
    printer_print_action = PrinterAction(_name=ActionName.PRINTER_PRINT)
    get_img_action = GetImgAction(_name=ActionName.GET_IMG)

    tasks = {

        TaskName.WEIGHT: Task(_name='称重',
                              _task=TaskName.WEIGHT,
                              _actions=[
                                  plate_in_action,
                                  plate_down_action,
                                  weight_action,
                                  plate_up_action,
                              ]),
        TaskName.WEIGHT_ZERO: Task(_name='称重清零【去皮】',
                                   _task=TaskName.WEIGHT_ZERO,
                                   _actions=[
                                       plate_in_action,
                                       plate_down_action,
                                       weight_action,
                                       plate_up_action,
                                   ]),
        TaskName.PLATE_OPEN: Task(_name='开启托盘',
                                  _task=TaskName.PLATE_OPEN,
                                  _actions=[
                                      plate_up_action,
                                      plate_out_action
                                  ]),
        TaskName.PLATE_CLOSE: Task(_name='关闭托盘',
                                   _task=TaskName.PLATE_OPEN,
                                   _actions=[
                                       plate_up_action,
                                       plate_in_action
                                   ]),
        TaskName.LIGHT_ON: Task(_name='开顶灯',
                                _task=TaskName.LIGHT_ON,
                                _actions=[
                                    light_on_action
                                ]),
        TaskName.LIGHT_OFF: Task(_name='关顶灯',
                                 _task=TaskName.LIGHT_OFF,
                                 _actions=[
                                     light_off_action
                                 ]),
        TaskName.PLATE_LIGHT_ON: Task(_name='开冷光片',
                                      _task=TaskName.PLATE_LIGHT_ON,
                                      _actions=[
                                          light_on_action
                                      ]),
        TaskName.PLATE_LIGHT_OFF: Task(_name='关冷光片',
                                       _task=TaskName.PLATE_LIGHT_OFF,
                                       _actions=[
                                           light_off_action
                                       ]),
        TaskName.FAN: Task(_name='开风扇',
                           _task=TaskName.FAN,
                           _actions=[
                               fan_action
                           ]),
        TaskName.SET_IP_PORT: Task(_name='设置静态IP和端口',
                                   _task=TaskName.SET_IP_PORT,
                                   _actions=[
                                       ip_port_action
                                   ]),
        TaskName.UPDATE_PRINTER_STATE: Task(_name='查询打印机状态',
                                            _task=TaskName.UPDATE_PRINTER_STATE,
                                            _actions=[
                                                printer_state_action
                                            ]),
        TaskName.PRINTER_PRINT: Task(_name='打印结果',
                                     _task=TaskName.PRINTER_PRINT,
                                     _actions=[
                                         printer_print_action
                                     ]),
        TaskName.PRINTER_RESTART: Task(_name='重启打印机',
                                       _task=TaskName.PRINTER_RESTART,
                                       _actions=[
                                           printer_restart_action
                                       ]),

        TaskName.EASY_MODE: Task(_name='自动模式',
                                 _task=TaskName.EASY_MODE,
                                 _actions=[
                                     # 进料
                                     plate_in_action,
                                     # 开对应的灯
                                     light_on_action,
                                     # 拍摄图片
                                     get_img_action,
                                     # 关灯
                                     light_off_action,
                                     # 图像分析 脚本形式
                                     # 下降
                                     plate_down_action,
                                     # 称重
                                     weight_action,
                                     # 抬升复位
                                     plate_up_action,
                                     # 读取算法数据 存档

                                     # 等待算法结束 打印结果
                                     printer_print_action,
                                 ])

    }
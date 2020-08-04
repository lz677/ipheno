#! C:\Users\93715\Anaconda3\python.exe
# *-* coding:utf8 *-*
"""
@author: Zhiyu YANG, Liu Zhe
@license: (C) Copyright SJTU ME
@contact: zhiyu_yang@sjtu.edu.cn, LiuZhe_54677@sjtu.edu.cn
@file: app_config.py
@time: 2020/7/28 19:47
@desc: LESS IS MORE
"""
# 三方库
from __future__ import annotations
from flask.json import jsonify
from threading import Lock, Thread, Event
from typing import List, NewType

import time
import abc
import os
import logging.config
import logging

# 自开发库
from hardware import WORK_ON_RPI

if WORK_ON_RPI:
    pass

# 日志配置
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../doc/conf/logging.conf')
logging.config.fileConfig(path)
logger = logging.getLogger('iphenoDebug')

StatesType = NewType('StatesType', str)


class States:
    COMPLETE = StatesType('complete')
    ERROR = StatesType('error')
    TERMINATE = StatesType('terminate')

    FISHING = StatesType('fishing')
    RUNNING = StatesType('running')


class StdResponse:
    def __init__(self, _name: str):
        self.name = _name
        self.states = States.FISHING
        self.error_desc = ''

        self.lock = Lock()

    def set_states(self, _states: StatesType, _error_desc: str = ''):
        with self.lock:
            self.states = _states
            self.error_desc = _error_desc

    def get_dict(self):
        with self.lock:
            return {
                'name': self.name,
                'status': self.states,
                'errorDesc': self.error_desc
            }

    def get_json(self):
        return jsonify(self.get_dict())


class ActionBase:
    def __init__(self, _name: str):
        self.name = _name
        self.states_resp = StdResponse(_name=_name)
        self.lock = Lock()
        self.will_terminate = False

    def fishing(self):
        if self.states_resp.states != States.ERROR:
            self.states_resp.set_states(States.FISHING)

    @abc.abstractmethod
    def run(self, task_name):
        raise NotImplementedError("Must override ActionBase.run()")

    def start(self, task_name):
        logger.info('执行%s...' % self.name)
        self.states_resp.set_states(States.RUNNING)
        self.run(task_name)
        logger.info('--- 执行%s结束' % self.name)
        return self.states_resp

    def terminate(self):
        with self.lock:
            self.will_terminate = True

    def check_will_terminate(self):
        with self.lock:
            if self.will_terminate:
                self.will_terminate = False
                return True
            return False

    def toggle_terminate(self):
        with self.lock:
            self.will_terminate = False


class TaskResponse:
    def __init__(self, _name: str, _action_names: List[str]):
        self.name = _name
        self.action_names = _action_names
        self.states: StatesType = States.FISHING
        self.action_states_dict = []
        self.error_desc = ''

        self.lock = Lock()

    def set_states(self, _states: StatesType, _error_desc: str = ''):
        with self.lock:
            self.states = _states
            self.error_desc = _error_desc

    def update_action_states(self, _action_states_dict: List[dict]):
        with self.lock:
            self.action_states_dict = _action_states_dict

    def get_task_states(self):
        return self.states

    def get_json(self):
        with self.lock:
            return jsonify({
                'name': self.name,
                'actionNames': self.action_names,
                'actionStatus': self.action_states_dict,
                'status': self.states,
                'errorDesc': self.error_desc
            })


class Task:
    def __init__(self, _name: str, _actions: List[ActionBase], _task: str):
        self.name = _name
        self.task = _task
        self.actions: List[ActionBase] = _actions
        self.states_resp = TaskResponse(_name, [_action.name for _action in _actions])

        self.e = Event()
        self.t = Thread()
        self.t.start()

    def start(self) -> TaskResponse:
        logger.info('开始执行任务<%s>' % self.name)
        self.states_resp.update_action_states([])
        if not self.t.is_alive():
            self.t = Thread(target=self.__run)
            self.states_resp.set_states(States.RUNNING)
            logger.info('--- 任务<%s>可执行，执行线程启动' % self.name)
            self.e.clear()
            self.t.start()
        else:
            logger.warning('--- 任务<%s>已经在执行，不可重复执行' % self.name)
            self.states_resp.set_states(States.ERROR, _error_desc='尚未结束上次运行')
        return self.states_resp

    def __run(self, **kwargs) -> bool:
        logger.info('--- 检查任务<%s>各动作状态:' % self.name)

        for _index, _action in enumerate(self.actions):
            logger.info('------ (%d) %s: %s' % (_index + 1, _action.name, _action.states_resp.states))
            if _action.states_resp.states == States.ERROR:
                self.states_resp.set_states(States.ERROR, _error_desc="%s 无法执行" % _action.name)
                logger.error('--- 任务<%s>未执行, 由于动作"%s"故障' % (self.name, _action.name))
                self.e.set()
                return False
            _action.fishing()

        for _action in self.actions:
            _action.start(self.task)
            self.states_resp.update_action_states([_action.states_resp.get_dict() for _action in self.actions])
            if _action.states_resp.states in (States.ERROR, States.TERMINATE):
                logger.error('--- 任务<%s>执行中止, 由于动作"%s"故障' % (self.name, _action.name))
                if _action.states_resp.states == States.ERROR:
                    self.states_resp.set_states(States.ERROR, _error_desc="%s 故障" % _action.name)
                    self.cancel()
                    self.e.set()
                elif _action.states_resp.states == States.TERMINATE:
                    self.states_resp.set_states(States.TERMINATE, _error_desc="%s 被中止" % _action.name)
                    _action.terminate()
                return False
            # elif _action.states_resp.states == States.RUNNING:
            #     logger.warning('--- 任务<%s>执行中, 动作"%s"仍在执行' % (self.name, _action.name))
            #     self.states_resp.set_states(States.RUNNING, _error_desc="%s 正在执行" % _action.name)
            #     self.e.set()
            else:
                self.e.set()
        # time.sleep(0.1)
        # print(self.t.is_alive())
        # if self.t.is_alive():
        #     self.t.join()
        logger.info('--- 任务<%s>完成' % self.name)
        self.states_resp.set_states(States.COMPLETE)
        self.e.set()
        return True

    def wait_for_states_update(self) -> TaskResponse:
        self.e.wait()
        self.e.clear()
        return self.states_resp

    def get_states(self) -> TaskResponse:
        return self.states_resp

    def cancel(self) -> TaskResponse:
        for _action in self.actions:
            _action.terminate()
        # print(self.t.is_alive())
        self.t.join()
        for _action in self.actions:
            _action.toggle_terminate()
        self.states_resp.set_states(States.TERMINATE)
        logger.info('--- 任务<%s>已取消' % self.name)
        # logger.info('--- 任务<%s>已取消, 开始执行重置任务' % self.name)
        # TaskManager.tasks['reset_' + self.name].start()
        return self.states_resp

    def __del__(self):
        if self.t.is_alive():
            self.cancel()

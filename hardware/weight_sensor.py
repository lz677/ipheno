#! C:\Users\93715\Anaconda3\python.exe
# *-* coding:utf8 *-*
"""
@author: LiuZhe
@license: (C) Copyright SJTU ME
@contact: LiuZhe_54677@sjtu.edu.cn
@file: weight_sensor.py
@time: 2020/7/15 21:32
@desc: LESS IS MORE
"""
import time
from hardware import Uart
import numpy as np
from app_task import gl_weight_stop

"""
主控板：5V 300mA

相关参数 GW502
实际分度值（g）           0.01
最大称量（g）              50
校准砝码（g）              50
最大允许误差（mg）          ±1
谷粒称重装置尺寸（mm）   340x195x106

参数设置：
通讯接口： RS-232
波特率： 115200 bps
数据位： 8 bit
停止位： 1 bit
校验： None

字符定义                    ASCII        HEX
查询当前称量值                 D         0X44
恢复出厂设置                   F         0X46
重启                         R         0X52
置零、取消当前置零命令          Z         0X5A
校准、取消当前校准命令          C         0X43

返回数据示例  
            称重          b'+      0.18 g \r\n'
            重启
            清零          b'Zero Done !\r\n\r\n' 
            无法解析       Bad Command.
"""


class WeightSensor(object):
    def __init__(self, uart_service: str = '/dev/ttyAMA0'):
        self.max_value = 50
        self.bps = 115200
        self.weight = -1
        self.receive = b''
        self.uart = Uart(bps=self.bps, device_tty=uart_service)

    def get_one_weight(self, timeout: float = 1) -> float:
        """
        获取智能考种仪的称重数据
            官方文档：
            查询当前称量值：【D】，HEX（0x44）
            示例：
            上位机发送： D
            模块返回： - 0.0027g 返回称量值：-0.0027g
            说明：称量不稳定时，返回数据中单位为空。
        :return: 单次称重 重量
        """
        # 接受的流 存下来
        self.receive = self.uart.send_and_receive(b'D', timeout=timeout, one_time=False)
        # TODO：注释print()
        # print('recv: ', self.receive)
        # 将流转化为字符串 格式类似b'+      0.18 g \r\n'
        recv = str(self.receive)
        # 定位到'g'说明测量正常
        # 说明书：称量不稳定时，返回数据中单位为空
        # TODO：若测量存在负值，处理负值。
        location = recv.find('g')
        if location != -1:
            # 以'g'的位置 定位数据位置
            weigh_str = recv[location - 7: location].strip()
            # 记录
            # self.weight = float(weigh_str)
            # TODO：注释print()
            # print("称重结果为： ", float(weigh_str))
            # 返回结果
            return float(weigh_str)
        else:
            # print("报错")
            return -666.666

    def zero_weight(self, timeout=3) -> bool:
        """
        清零或去皮
        :rtype: 是否清零成功
        """
        zero_weight_message = self.uart.send_and_receive(b'Z', timeout=timeout)
        # 查看收到数据
        # print('recv: ', zero_weight_message)
        if 'Zero Done' in str(zero_weight_message):
            return True
        return False

    def get_weight(self, measure_times: int = 5):
        times = 0
        weights_list = np.zeros(measure_times)
        print('测量%d次，当前测量次数为：' % measure_times, end=' ')
        while times < measure_times and not gl_weight_stop:
            weight = self.get_one_weight()
            if weight != -666.666:
                print(times + 1, end=' ')
                weights_list[times] = weight
                times += 1
            time.sleep(0.1)
        self.weight = weights_list.mean()
        return weights_list.mean(), weights_list.std()

    def test(self, w_sen):
        print('清零中...')
        while True:
            # TODO：测量10次计算平均值 和 均方差
            #       树莓派解决读不到base包的问题
            a = w_sen.zero_weight()
            if a:
                break
        # time.sleep(2)
        print('当前重量：', w_sen.get_one_weight(5))
        input('清零完成，请放置物品后按回车开始测量:')
        # print('单次测量： ', w_sen.get_one_weight(5))
        print("测量中...")
        b, c = w_sen.get_weight()
        print()
        print('测量结果为：')
        print('%.3f +- %.3f g' % (b, c))


if __name__ == '__main__':
    ws = WeightSensor(uart_service='COM5')
    try:
        ws.test(ws)
    except KeyboardInterrupt:
        print('程序中断')

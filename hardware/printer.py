#! C:\Users\93715\Anaconda3\python.exe
# *-* coding:utf8 *-*
"""
@author: LiuZhe
@license: (C) Copyright SJTU ME
@contact: LiuZhe_54677@sjtu.edu.cn
@file: printer.py
@time: 2020/7/24 10:06
@desc: LESS IS MORE
"""
from hardware import uart

"""
200dpi: 1 mm = 8 dot
"""


class Printer(object):
    def __init__(self, tty='/dev/ttyUSB1'):
        self.uart = uart.Uart(tty, 9600)
        self.status = 0
        self.grain_para_en = {}
        self.panicle_para_en = {}
        self.grain_para_ch = {'品种号': '袁1品',
                              '总粒数': '35',
                              '千粒重': '100 g',
                              '实粒质量': '10 g',
                              '粒长度平均值': '2 cm',
                              '粒宽度平均值': '1 cm',
                              '粒长宽比平均值': '2'
                              }
        self.panicle_para_ch = {'品种号': 'NONE',
                                '穗长': 'NONE',
                                '实粒数': 'NONE',
                                '瘪粒数': 'NONE',
                                '一次支梗数': 'NONE',
                                '节间长度平均值': 'NONE'
                                }

    # 将打印的参数封装成一个字符串
    # 简体中文字体为 24 * 24 dot  200dpi: 1 mm = 8 dot
    # 单张纸最多打印7的参数，封装一张
    def __set_print_para_mes(self, para_mes: dict, is_english: bool) -> str:
        font = "\"3\"" if is_english else "\"TSS24.BF2\""
        paras_str = ''
        if len(para_mes) <= 7:
            num_of_para = 0
            for para in para_mes:
                y_position = str(240 - 15 - num_of_para * 30)
                paras_str += ("TEXT 290," + y_position + "," + font + ",180,1,1," + "\"" + para + ": " +
                              para_mes[para] + "\"" + "\r\n")
                num_of_para += 1
                if num_of_para == len(para_mes):
                    break
            return paras_str
        else:
            return paras_str

    # 打印机 打印封装
    def __printer_print_str(self, print_para_mes: dict, is_english: bool) -> str:
        print_messages: str = ("SIZE 40 mm,30 mm\r\n" +  # 卷纸 宽和长度  320 * 240 dot
                               "GAp 2.1 mm,0 mm\r\n" +  # 卷纸垂直距离
                               "SpEED 1.0\r\n" +  # 打印速度
                               "DENSITY 7\r\n" +  # 打印浓度
                               "DIRECTION 0,0\r\n" +  # 打印方向 顺着出纸方向为正
                               "REFERENCE 0,0\r\n" +  # 坐标原点 右下为零点
                               "OFFSET 0 mm\r\n" +  # 用于剥离模式每张卷标停止的位置，仅用于剥离模式
                               "SHIFT 0\r\n" +  # 打印偏移量 -203<n<203
                               "SET pEEL OFF\r\n" +  # 关闭剥离模式
                               "SET CUTTER OFF\r\n" +
                               "SET pARTIAL_CUTTER OFF\r\n" +
                               "SET TEAR ON\r\n" +  # 启用撕纸位置走到撕纸处
                               "CLS\r\n" +  # 清除影像缓冲区的数据
                               "CODEpAGE 850\r\n" +  # 选择对应的国际字集
                               self.__set_print_para_mes(print_para_mes, is_english)
                               +
                               "PRINT 1\r\n"
                               )
        return print_messages

    def printer_restart(self):
        self.uart.send_and_receive(b'\x1b\x21\x52')
        status: bytes = self.uart.send_and_receive(b'\x1b\x21\x3f', one_time=False)
        print("打印机返回数据", status)

        print(int.from_bytes(status, 'little'))

    # 询问打印机状态
    def printer_states(self):
        """
        bit             状态
        0               打印机未关闭
        1               卡纸
        2               缺纸
        3               无碳带
        4               暂停打印
        5               打印中
        6               机壳未关闭
        7               错误
        :return:
        """
        # TODO: 根据返回值获取结果 返回对应的数值

        status: bytes = self.uart.send_and_receive(b'\x1b\x21\x3f', one_time=False)
        print("打印机返回数据", status)

        # print(int.from_bytes(status, 'little'))
        # print("打印机返回数据转化为整形", int(status))
        return int.from_bytes(status, 'little')

    # 打印参数
    def printer_print(self, all_parameters: dict, is_english: bool):
        # 参数应该打多少张
        pages_num = (len(all_parameters) // 7 + (len(all_parameters) % 7 != 0))
        if pages_num:
            page = 1
            while page <= pages_num:
                para_num = 0
                para_dic = {}
                for para in all_parameters:
                    # 判断个数，满7 或者 不超过7个但已经没有了
                    if para_num < 7 and para_num != len(all_parameters):
                        para_dic.update({para: all_parameters[para]})
                        para_num += 1
                    else:
                        break
                # 打印
                # print("para_dic", para_dic)
                # TODO: 调通串口的send函数
                self.uart.send_message(self.__printer_print_str(para_dic, is_english).encode('gbk'))
                # print(self.__printer_print_str(para_dic, is_english).encode())
                # print(self.__printer_print_str(para_dic, is_english))

                # 剔除已经打印完成的
                for para in para_dic:
                    all_parameters.pop(para)

                # 下一张
                page += 1
            return True
        else:
            print("没有要打印的参数")
            return False

    # 设置要打印的谷粒参数
    def set_grain_paras(self, grain_paras: dict):
        self.grain_para_ch = grain_paras

    # 设置要打印的稻穗参数
    def set_panicle_paras(self, panicle_paras: dict):
        self.panicle_para_ch = panicle_paras

    # 打印默认的谷粒参数
    def print_grain(self, is_english=False):
        self.printer_print(self.grain_para_en, True) if is_english else self.printer_print(self.grain_para_ch, False)

    # 打印默认的稻穗参数
    def print_panicle(self, is_english=False):
        self.printer_print(self.grain_para_en, True) if is_english else self.printer_print(self.panicle_para_ch, False)


if __name__ == '__main__':
    printer = Printer()
    print("测试打印机")
    print("测试查询状态 返回数据格式")
    printer.printer_restart()
    # print('*' * 50)
    # print("打印测试")
    # # printer.print_grain()
    # # print('*' * 50)
    # # printer.print_panicle()
    # print('*' * 50)
    # printer.printer_print({'大妈你看': '成功了',
    #                        '品种号': '袁1品',
    #                        '总粒数': '35',
    #                        '千粒重': '100 g',
    #                        '实粒质量': '10 g',
    #                        '粒长度平均值': '2 cm',
    #                        '粒宽度平均值': '1 cm',
    #                        '粒长宽比平均值': '2',
    #                        '总粒数2': '70',
    #                        '千粒重2': '120 g',
    #                        '实粒质量2': '15 g',
    #                        '粒长度平均值2': '2 cm',
    #                        '粒宽度平均值2': '1 cm',
    #                        '粒长宽比平均值2': '2'
    #                        }, False)

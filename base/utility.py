#!/usr/bin/env python
# encoding: utf-8

"""
@version: Python3.7
@author: Zhiyu YANG, Liu Zhe
@e-mail: zhiyu_yang@sjtu.edu.cn, LiuZhe_54677@sjtu.edu.cn
@file: utility.py
@time: 2020/5/5 17:12

Code is far away from bugs with the god animal protecting
"""
import psutil
import pickle
import json
import os
from base import hard


def save_data(filename: str, data):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)


def load_data(filename: str):
    with open(filename, 'rb') as f:
        return pickle.load(f)


def is_ipv4(ip: str) -> bool:
    """
    检查ip是否合法
    :param: ip ip地址
    :return: True 合法 False 不合法
    """
    return True if [1] * 4 == [x.strip().isdigit() and 0 <= int(x.strip()) <= 255 for x in ip.split(".")] else False


def is_port(port: str, protocol: str = 'http') -> bool:
    """
    检测port是否是合法的协议代理服务器常用端口号
    :param protocol: http ftp socks Telnet
    :param port: 端口号
    :return: True 端口号是'80', '8080', '3128', '8081', '9098'中一个 False 不可用
    """
    port = port.strip()
    if protocol.lower() == 'http':
        return True if port.isdigit() and port in ('8080', '3128', '8081', '9098', '5000', '8000') else False
    elif protocol.lower() == 'ftp':
        return True if port.isdigit() and port in ('21',) else False
    elif protocol.lower() == 'socks':
        return True if port.isdigit() and port in ('1080',) else False
    elif protocol.lower() == 'telnet':
        return True if port.isdigit() and port in ('23',) else False
    else:
        return False


def is_img(name: str) -> bool:
    # return name.lower().endswith(('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff'))
    return name.lower().endswith(('.bmp', '.png', '.jpg', '.jpeg', '.pbm'))


def save_info_to_json(hardware_instance, path: str) -> bool:
    main_control_info = {
        'all_status': hardware_instance.get_all_states(),
        'system_info': hardware_instance.get_system_info(),
        'error_info': hardware_instance.get_error_info()
    }
    try:
        with open(path, 'w', encoding='UTF-8') as j_f:
            j_f.write(json.dumps(main_control_info))
        return True
    except IOError as ioerr:
        print("文件 %s 无法创建" % path)
        return False


def read_info_from_json(hardware_instance, path: str = './config/main_control.json') -> bool:
    try:
        with open(path, 'r') as j_f:
            main_control_info = json.load(j_f)
        hardware_instance.system_info = main_control_info['system_info']
        hardware_instance.all_states = main_control_info['all_status']
        hardware_instance.error_info = main_control_info['error_info']
        return True
    except IOError as ioerr:
        print("%s 无配置文件" % path)
        return False


def update_file(file: bytes, file_path):
    with open(file_path, 'wb') as f:
        f.write(file)
    print("更新完毕")
    return True


def update_project(new_path, version_info='', project_name='ipheno-server.tar.gz'):
    # os.system('cd ' + new_path)
    # logger.info(version_info)
    try:
        # 解压
        os.system('tar -zcvf ' + new_path + '/' + project_name + ' ipheno-server')
    except:
        pass
    os.system('mv ' + new_path + '/ipheno-server /home/pi/Documents/ipheno-server/ipheno-server')


def network_setup(ip_add, net_mask, broad_add):
    os.system('sudo ifconfig eth0 down')
    os.system('sudo ifconfig eth0 ' + ip_add)
    # os.system('sudo ifconfig eth0 netmask ' + net_mask)
    # os.system('sudo ifconfig eth0 broadcast ' + broad_add)
    os.system('sudo ifconfig eth0 up')


def check_if_process_running(process_name):
    # Iterate over all the running process
    for proc in psutil.process_iter():
        try:
            # heck if process name contains the given name string
            if process_name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            print("denied")
            pass
    return False


def find_process_id_by_name(process_name, only_pid=False):
    list_of_process_objects = []
    # Iterate over all the running process
    for proc in psutil.process_iter():
        try:
            p_info = proc.as_dict(attrs=['pid', 'name', 'create_time'])
            # check if process name contains the given name string
            if process_name.lower() in p_info['name'].lower():
                list_of_process_objects.append(p_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return list_of_process_objects

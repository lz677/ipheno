#! C:\Users\93715\Anaconda3\python.exe
# *-* coding:utf8 *-*
"""
@author: Liu Zhe, Zhiyu YANG
@license: (C) Copyright SJTU ME
@contact: LiuZhe_54677@sjtu.edu.cn, zhiyu_yang@sjtu.edu.cn
@file: app.py
@time: 2020/7/28 19:36
@desc: LESS IS MORE
"""
# 三方库
from flask import Flask, Response, request
from flask.json import jsonify
import time
import os
import sys
# 开发库
from base import HardwareStates, utility
from app_config.app_conf import logger
from app_config.app_task import TaskManager, hardware_info, results_info

# flask 标识
app = Flask(__name__)


@app.errorhandler(404)
def error404(args):
    return args


# 动作任务路由
@app.route('/task/<string:task_name>')
def task(task_name: str):
    logger.info('收到任务<%s>执行请求' % task_name)
    if 'fan' in task_name:
        try:
            hardware_info.all_states[HardwareStates.fan] = int(request.args.get('duty'))
            logger.debug('---- 风扇开度设置为：%d' % hardware_info.all_states[HardwareStates.fan])
        except TypeError:
            hardware_info.all_states[HardwareStates.fan] = 10
            logger.warning('未设置风扇开度(duty) 将其默认开启最低值10')
    if 'set-ip' in task_name:
        try:
            hardware_info.system_info['temIP']['ip'] = request.args.get("ip")
            hardware_info.system_info['temIP']['port'] = request.args.get("port")
        except KeyError:
            logger.warning('未设置ip和端口，将其默认为初始值')
            hardware_info.system_info['temIP']['ip'] = '192.168.1.7'
            hardware_info.system_info['temIP']['port'] = '5000'
    # time.sleep(1)
    return TaskManager.tasks[task_name].start().get_json()


@app.route('/task-cancel/<string:task_name>')
def task_cancel(task_name: str):
    logger.warning('收到取消任务<%s>请求' % task_name)
    return TaskManager.tasks[task_name].cancel().get_json()


@app.route('/task-progress/<string:task_name>')
def task_progress(task_name: str):
    return TaskManager.tasks[task_name].wait_for_states_update().get_json()


@app.route('/task-result/<string:task_name>')
def task_result(task_name: str):
    only_data = True
    if task_name == 'weight':
        return jsonify({
            '称重结果': hardware_info.all_states[HardwareStates.balance]
        })
    if task_name == 'weight-zero':
        return jsonify({
            '清零成功': ' '
        })
    if task_name == 'image':
        img_result = {}
        for res in results_info.img_info:
            if results_info.img_info[res] != 'NONE':
                img_result.update({res: results_info.img_info[res]})
        return jsonify(img_result)

    if only_data:
        results = {}
        if task_name in ('weight', 'easy-mode-grain'):
            results.update({'重量': hardware_info.all_states[HardwareStates.balance]})
        for res in results_info.img_parameters:
            if results_info.img_parameters[res] != 'NONE':
                results.update({res: results_info.img_parameters[res]})
        img_result = []
        for res in results_info.img_info:
            if results_info.img_info[res] != 'NONE':
                img_result.append(res)
                img_result.append(results_info.img_info[res])
        results.update({'image': img_result})
        # results.update(results_info.get_image_info())
        logger.debug(results)
        return jsonify(results)
    # 返回结果
    cal_results = results_info.get_image_parameters()
    # 算法返回的图片 以 base64 的方式 存储在 imageBase64的属性里。
    cal_results.update(results_info.get_image_info())
    return jsonify(results_info.get_image_parameters())


# 主控状态路由
# 实时图像
@app.route('/img/<string:image_name>')
def img_realtime(image_name):
    if not hardware_info.capture.is_opened():
        hardware_info.capture.open()
    hardware_info.capture.start_stream()
    # app web端
    if image_name.endswith(".jpg"):
        logger.debug('--- 前端请求jpg')
        return Response(hardware_info.capture.gen_stream(), mimetype="image/jpg")
    elif image_name.endswith(".png"):
        logger.debug('--- 前端请求png')
        return Response(hardware_info.capture.gen_stream(False), mimetype="image/png")
    # web 端
    elif image_name == 'realtime':
        logger.debug('--- 前端请求实时流')
        return Response(hardware_info.capture.gen_stream_web(), mimetype='multipart/x-mixed-replace; boundary=frame')


# 硬件状态
@app.route('/states/<string:cmd>')
def states(cmd='all'):
    if cmd == 'all':
        logger.info('--- 查询外设整体状态')
        return jsonify(hardware_info.get_all_states())
    elif cmd in (HardwareStates.camera, HardwareStates.balance, HardwareStates.printer, HardwareStates.main,
                 HardwareStates.plate_down, HardwareStates.plate_out, HardwareStates.light, HardwareStates.light_plate,
                 HardwareStates.fan):
        logger.info('--- 查询<%s>状态，其状态为<%s>' % (cmd, hardware_info.all_status[cmd]))
        return jsonify({cmd: hardware_info.all_status[cmd]})


# 总控信息
@app.route('/system/<string:cmd>')
def system(cmd: str):
    if utility.save_info_to_json(hardware_info, './doc/conf/main_control.json'):
        logger.info("--- 主控配置储存成功 ---")
    else:
        logger.error('--- 主控配置未能成功储存 ---')
    if cmd == 'info':
        logger.debug('--- 查询总控信息')
        return jsonify(hardware_info.get_system_info())
    elif cmd == 'restart':
        time.sleep(1)
        # 重启服务器代码
        logger.warning("--- 重启服务器 ---")
        os.execv(sys.executable, ['python -m flask run'] + sys.argv)
    elif cmd == 'reboot':
        time.sleep(1)
        logger.warning("--- 重启总控 ---")
        os.system('sudo reboot')


# 更新版本 TODO: 需要获取app端传递文件 本机先测试 解压和覆盖问题
@app.route('/update-project')
def update_project():
    logger.warning('--- 更新本地版本')
    utility.update_project('/home/pi/Documents/hh')


# from app_config.app_task import drawer_hard, light_hard, fan_hard, lifting_hard


# app端
@app.route('/plate/<string:cmd>')
def plate(cmd):
    """
    open or close the plate
    :param cmd: open close
    :return: ok failed 404 [check you url]
    """
    # print("plate:", cmd)
    if cmd == "open":
        TaskManager.tasks['plate-open'].start()
        return jsonify({'state': "failed"}) if TaskManager.tasks['plate-open'].get_states().states == 'complete' \
            else jsonify({'state': "ok"})
    elif cmd == "close":
        TaskManager.tasks['plate-close'].start()
        return jsonify({'state': "ok"}) if TaskManager.tasks['plate-close'].get_states().states == 'complete' \
            else jsonify({'state': "failed"})
    else:
        # print("检查你的url")
        return jsonify({"error": "404 [check you url]"})


@app.route('/light/<string:cmd>')
def light(cmd):
    if cmd == "open":
        TaskManager.tasks['light-on'].start()
        return jsonify({'state': "failed"}) if TaskManager.tasks['light-on'].get_states().states == 'complete' \
            else jsonify({'state': "ok"})
    elif cmd == "close":
        TaskManager.tasks['light-off'].start()
        return jsonify({'state': "ok"}) if TaskManager.tasks['light-off'].get_states().states == 'complete' \
            else jsonify({'state': "failed"})
    else:
        # print("检查你的url")
        return jsonify({"error": "404 [check you url]"})


@app.route('/plate-light/<string:cmd>')
def plate_light(cmd):
    if cmd == "open":
        TaskManager.tasks['plate-light-on'].start()
        time.sleep(0.1)
        return jsonify({'state': "failed"}) if TaskManager.tasks['plate-light-on'].get_states().states == 'complete' \
            else jsonify({'state': "ok"})
    elif cmd == "close":
        TaskManager.tasks['plate-light-off'].start()
        time.sleep(0.1)
        return jsonify({'state': "ok"}) if TaskManager.tasks['plate-light-off'].get_states().states == 'complete' \
            else jsonify({'state': "failed"})
    else:
        # print("检查你的url")
        return jsonify({"error": "404 [check you url]"})


@app.route('/fan')
def fan():
    try:
        hardware_info.all_states[HardwareStates.fan] = int(request.args.get('duty'))
        logger.debug('---- 风扇开度设置为：%d' % hardware_info.all_states[HardwareStates.fan])
    except TypeError:
        hardware_info.all_states[HardwareStates.fan] = 10
        logger.warning('未设置风扇开度(duty) 将其默认开启最低值10')
    TaskManager.tasks['fan'].start()
    time.sleep(0.1)
    return jsonify({'state': "ok"}) if TaskManager.tasks['fan'].get_states().states == 'complete' \
        else jsonify({'state': "failed"})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

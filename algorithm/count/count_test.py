#! /usr/bin/python3
# ================================================================
#   Copyright (C) 2020 * Ltd. All rights reserved.
#
#   Project     : count
#   File name   : count_test.py
#   Author      : Fan Shengzhe
#   Created date: 2020/7/26 18:02
#   Editor      : PyCharm 2019.1
#   Description :
#
# ================================================================

import dlcount
import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import time
import logging
import json

logging.basicConfig(level=logging.DEBUG)
start = time.time()
# read image
path = '/home/pi/Documents/ipheno/static/count.jpg'
# input_img = cv2.imread(os.path.join(dlcount.config.IMG_PATH, 'example1.jpg'))
input_img = cv2.imread(path)
input_img = input_img.transpose((1, 0, 2))[:, ::-1, :]
input_img = input_img[600:-300, 300:-550, :]
input_img = input_img[..., [2, 1, 0]]  # BGR -> RGB

# inference
splice_splice = dlcount.split_splice.SplitSplice(input_img)
input_batch = splice_splice.split(input_img)
output_batch = dlcount.segment(input_batch)
output_img = splice_splice.splice(output_batch)
result, num = dlcount.merge_count(input_img, output_img[..., -1])
logging.info(f'{num} particles have been found,\n{time.time() - start} seconds have been taken.')
# visualization
# result = cv2.imencode('.png', result)
result = cv2.rotate(result, cv2.ROTATE_90_COUNTERCLOCKWISE)
cv2.imwrite('/home/pi/Documents/ipheno/static/count_result.png', result)

# num 结果存为json
result_path = '/home/pi/Documents/ipheno/algorithm/results/count_result.json'
try:
    with open(result_path, 'w', encoding='UTF-8') as j_f:
        j_f.write(json.dumps({'num': num}))
except IOError as ioerr:
    print("文件 %s 无法创建" % result_path)

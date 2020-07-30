# ================================================================
#   Copyright (C) 2020 * Ltd. All rights reserved.
#
#   Project     : count
#   File name   : config.py
#   Author      : Fan Shengzhe
#   Created date: 2020/7/26 18:13
#   Editor      : PyCharm 2019.1
#   Description :
#
# ================================================================

import os

IMG_PATH = './dlcount/img'  # 按要求改为图片的目录！！
SCALE_FACTOR = 0.2          # deprecated
SPLIT_H = 650
SPLIT_W = 490
BATCH_SIZE = 40


PACKAGE_PATH = os.path.dirname(__file__)
TFLITE_FILE_PATH = os.path.join(PACKAGE_PATH, 'tflite_model')


# ================================================================
#   Copyright (C) 2020 * Ltd. All rights reserved.
#
#   Project     : count
#   File name   : merge_count.py
#   Author      : Fan Shengzhe
#   Created date: 2020/7/27 01:40
#   Editor      : PyCharm 2019.1
#   Description :
#
# ================================================================
import numpy as np
import cv2

def merge_count(img, label):
    mask = label > 0.5
    img[mask] = np.array([255, 0, 0])

    h = cv2.findContours(mask.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours = h[0]

    return img, len(contours)
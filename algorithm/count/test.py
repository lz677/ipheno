# ================================================================
#   Copyright (C) 2020 * Ltd. All rights reserved.
#
#   Project     : count
#   File name   : test.py
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

start = time.time()
# read image
input_img = cv2.imread(os.path.join(dlcount.config.IMG_PATH, 'example1.jpg'))
input_img = input_img[..., [2, 1, 0]]  # BGR -> RGB

# inference
splice_splice = dlcount.split_splice.SplitSplice(input_img)
input_batch = splice_splice.split(input_img)
output_batch = dlcount.segment(input_batch)
output_img = splice_splice.splice(output_batch)
result, num = dlcount.merge_count(input_img, output_img[..., -1])
print(f'{num} particles have been found,\n{time.time() - start} seconds have been taken.')
# visualization
plt.imshow(result)
# plt.show()
print(f'{num} particles have been found,\n{time.time() - start} seconds have been taken.')

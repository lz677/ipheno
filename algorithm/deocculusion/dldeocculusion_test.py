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

import dldeocculusion
import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import time

start = time.time()
# read image
input_img = cv2.imread(os.path.join(dldeocculusion.config.IMG_PATH, '0.jpg'))
input_img = cv2.resize(input_img, (dldeocculusion.IMAGE_W, dldeocculusion.IMAGE_H))
input_img = input_img[np.newaxis, ..., [2, 1, 0]]  # BGR -> RGB

# inference
output_img = (dldeocculusion.inference(input_img) * 0.5 + 0.5)[0]

# visualization
# plt.imshow(output_img)
cv2.imwrite('results.jpg', output_img)
# plt.show()
print(f'{time.time() - start} seconds have been taken.')

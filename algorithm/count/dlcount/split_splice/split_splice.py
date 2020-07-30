# ================================================================
#   Copyright (C) 2020 * Ltd. All rights reserved.
#
#   Project     : count
#   File name   : split_splice.py
#   Author      : Fan Shengzhe
#   Created date: 2020/7/26 22:35
#   Editor      : PyCharm 2019.1
#   Description :
#
# ================================================================

import cv2
import matplotlib.pyplot as plt
import numpy as np
from ..config import *


class SplitSplice():
    def __init__(self, input_img):
        self.image_h, self.image_w = input_img.shape[:2]
        self.split_h = SPLIT_H
        self.split_w = SPLIT_W

        self.h_remainder = self.image_h % self.split_h
        self.w_remainder = self.image_w % self.split_w
        # ignore the situation of remainder == 0
        self.num_h = int(self.image_h / self.split_h) + 1
        self.num_w = int(self.image_w / self.split_w) + 1

    def split(self, input_img):
        patches = []
        for h_index in range(self.num_h - 1):
            for w_index in range(self.num_w - 1):
                patch = (input_img[h_index * self.split_h: (h_index + 1) * self.split_h,
                                   w_index * self.split_w:(w_index + 1) * self.split_w, ...])
                patches.append(patch)

            if self.w_remainder != 0:
                patch = (input_img[h_index * self.split_h: (h_index + 1) * self.split_h,
                                   (self.num_w - 1) * self.split_w:, ...])
                patch = cv2.resize(patch, (self.split_w, self.split_h))
                patches.append(patch)

        if self.h_remainder != 0:
            for w_index in range(self.num_w - 1):
                patch = (input_img[(self.num_h - 1) * self.split_h:,
                                   w_index * self.split_w:(w_index + 1) * self.split_w, ...])
                patch = cv2.resize(patch, (self.split_w, self.split_h))
                patches.append(patch)

                if self.w_remainder != 0:
                    patch = (input_img[(self.num_h - 1) * self.split_h:,
                                       (self.num_w - 1) * self.split_w:, ...])
                    patch = cv2.resize(patch, (self.split_w, self.split_h))
                    patches.append(patch)
        self.patch_num = len(patches)

        for padding_index in range(BATCH_SIZE - self.patch_num):
            padding = np.zeros((self.split_h, self.split_w, input_img.shape[2]))
            patches.append(padding)
        return np.stack(patches, axis=0)

    def splice(self, image):
        patches = iter([image[n] for n in range(image.shape[0])])
        output_img = np.zeros((self.image_h, self.image_w, image[0].shape[2]), dtype=image.dtype)
        for h_index in range(self.num_h - 1):
            for w_index in range(self.num_w - 1):
                patch = next(patches)
                output_img[h_index * self.split_h: (h_index + 1) * self.split_h,
                           w_index * self.split_w: (w_index + 1) * self.split_w, ...] += patch

            if self.w_remainder != 0:
                patch = next(patches)
                patch = cv2.resize(patch, (self.w_remainder, self.split_h))
                output_img[h_index * self.split_h: (h_index + 1) * self.split_h,
                           (self.num_w - 1) * self.split_w:, ...] = patch

        if self.h_remainder != 0:
            for w_index in range(self.num_w - 1):
                patch = next(patches)
                patch = cv2.resize(patch, (self.split_w, self.h_remainder))
                output_img[(self.num_h - 1) * self.split_h:,
                            w_index * self.split_w:(w_index + 1) * self.split_w, ...] = patch

                if self.w_remainder != 0:
                    patch = next(patches)
                    patch = cv2.resize(patch, (self.w_remainder, self.h_remainder))
                    output_img[(self.num_h - 1) * self.split_h:,
                               (self.num_w - 1) * self.split_w:, ...] = patch

        return output_img

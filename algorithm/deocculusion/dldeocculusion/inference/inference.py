# ================================================================
#   Copyright (C) 2020 * Ltd. All rights reserved.
#
#   Project     : count
#   File name   : inference.py
#   Author      : Fan Shengzhe
#   Created date: 2020/7/26 18:12
#   Editor      : PyCharm 2019.1
#   Description :
#
# ================================================================
from ..config import *
import tflite_runtime.interpreter as tflite
import os
import cv2
import numpy as np
from matplotlib import pyplot as plt


def get_newest_model():
    models_name = [name for name in os.listdir(TFLITE_FILE_PATH) if name[-7:] == '.tflite']
    models_name = sorted(models_name)
    # print(models_name[-1])
    return models_name[-1]

def resize_normalize(img):
    pass


def inference(input_img):
    # input_img should be BGR image of N * H * W * C format

    # Load the TFLite model and allocate tensors
    model_path = os.path.join(TFLITE_FILE_PATH, get_newest_model())
    interpreter = tflite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    # Get input and output tensors' details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    input_shape = input_details[0]['shape']

    # Read image and split it to patches
    # Resize according to the input shape requirement

    input_img = input_img.astype(np.float32) / 125 - 1

    # Inference
    interpreter.set_tensor(input_details[0]['index'], input_img)
    interpreter.invoke()
    output_img = interpreter.get_tensor(output_details[0]['index'])

    # Display the result
    # plt.imshow(output_img[0, ..., -1], cmap=plt.cm.gray_r)

    return output_img

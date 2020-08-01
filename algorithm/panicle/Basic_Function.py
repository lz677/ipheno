import cv2 as cv
import math


# 二值化函数
def binarization(img):
    # 灰度化
    gra = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # 高斯滤波
    blur = cv.GaussianBlur(gra, (5, 5), 0)
    # OSTU阈值分割
    ret, binary = cv.threshold(gra, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    if (ret > 100):
        ret, binary = cv.threshold(gra, 100, 255, cv.THRESH_BINARY_INV)
    # binary = cv.bitwise_not(binary)
    return binary


# 开运算
def open(img):
    g = cv.getStructuringElement(cv.MORPH_ELLIPSE, (9, 9))
    binary = cv.morphologyEx(img, cv.MORPH_OPEN, g)
    return binary


# 闭运算
def close(img):
    g = cv.getStructuringElement(cv.MORPH_ELLIPSE, (9, 9))
    binary = cv.morphologyEx(img, cv.MORPH_CLOSE, g)
    # binary = cv.bitwise_not(binary)
    return binary


def vp_and_median(numbers1):  # 计算极差和中位数
    numbers = sorted(numbers1)  # sorted(numbers)
    size = len(numbers)
    if size % 2 == 0:
        med = (numbers[size // 2 - 1] + numbers[size // 2]) / 2
    else:
        med = numbers[size // 2]
    vp = numbers[-1] - numbers[0]
    return vp, med


def dev_and_sdev(numbers, mean):  # 计算方差和标准差
    sdev = 0.0
    for num in numbers:
        sdev = sdev + (num - mean) ** 2
    dev = pow(sdev / (len(numbers) - 1), 0.5)
    sdev = math.sqrt(dev)
    return dev, sdev


def max_and_min(numbers1):  # 计算最大值和最小值
    numbers = sorted(numbers1)
    max = numbers[-1]
    min = numbers[0]
    return max, min


def aver(numbers):  # 计算平均值
    s = len(numbers)
    num = 0
    for n in numbers:
        num = num + n
    a = num / s
    return a

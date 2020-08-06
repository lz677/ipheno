#! /usr/bin/python3

import cv2 as cv
import numpy as np
import Basic_Function
import time
import logging
import json

logging.basicConfig(level=logging.DEBUG)


def calc(img, binary):
    result = []
    Area = []
    ID = []
    singleArea = []
    singleID = []
    cohesiveArea1 = []
    cohesiveID1 = []
    cohesiveArea = []
    cohesiveID = []
    minArea = 100  # 最小筛选面积
    contours, hierarchy = cv.findContours(binary, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    for i in range(len(contours)):
        temp = cv.contourArea(contours[i])
        if hierarchy[0, i, 2] != -1:  # 如果该连通域有子连通域，则多个粘连谷粒在中间形成了空腔，粘连谷粒有效面积=连通域面积-子连通域
            k = hierarchy[0, i, 2]
            cv.drawContours(img, contours, i, (0, 0, 255), 2)
            cv.drawContours(img, contours, k, (0, 0, 255), 2)
            cohesiveArea.append(temp - cv.contourArea(contours[k]))
            cohesiveID.append((i, k))
            continue
        if hierarchy[0, i, 3] != -1:  # 如果该连通域有父连通域，则是多个粘连谷粒形成的空腔，跳过
            continue
        if temp < minArea:  # 如果该连通域小于最小面积，则为杂质，剔除
            cv.drawContours(img, contours, i, (0, 255, 0), 2)
            continue
        Area.append(temp)
        ID.append(i)
    Area1 = Area
    Area2 = sorted(Area1)
    k = int(len(Area2) / 2)
    ave = sum(Area2[0:k]) / (k + 1)  # 连通域面积的中位数以下为独立谷粒，即独立谷粒数至少占一半，否则粘连谷粒太多，需减少谷粒数量重新测量
    for j in range(len(Area)):
        if Area[j] < 1.4 * ave:
            singleID.append(ID[j])
            singleArea.append(Area[j])
            cv.drawContours(img, contours, ID[j], (255, 0, 0), 2)
        else:
            cohesiveID1.append(ID[j])
            cohesiveArea1.append(Area[j])
    num = len(singleArea)
    ave = sum(singleArea[:]) / num
    for i in range(len(cohesiveArea1)):
        k = round(cohesiveArea1[i] / ave)
        if k < 2:
            singleID.append(cohesiveID1[i])
            singleArea.append(cohesiveArea1[i])
            cv.drawContours(img, contours, cohesiveID1[i], (255, 0, 0), 2)
        else:
            cohesiveID.append(cohesiveID1[i])
            cohesiveArea.append(cohesiveArea1[i])
            cv.drawContours(img, contours, cohesiveID1[i], (0, 0, 255), 2)
    single_num = len(singleArea)
    single_ave = sum(singleArea[:]) / single_num
    logging.info("独立谷粒数：" + str(single_num))
    cohesive_num = 0
    for area in cohesiveArea:
        cohesive_num = cohesive_num + round(area / single_ave)
    logging.info("粘连谷粒数：" + str(cohesive_num))
    num_all = single_num + cohesive_num
    logging.info("总谷粒数：" + str(num_all))
    result.append(num_all)
    length = []
    width = []
    ratio = []
    for id in singleID:
        min_rect = cv.minAreaRect(contours[id])
        rect_points = cv.boxPoints(min_rect)
        rect_points = np.int0(rect_points)
        cv.drawContours(img, [rect_points], 0, (0, 0, 0), 2)
        shape = [min_rect[1][0], min_rect[1][1]]
        shape = sorted(shape)
        width.append(shape[0])
        length.append(shape[1])
        ratio.append(shape[1] / shape[0])
    result.append(Basic_Function.calcList(length))
    result.append(Basic_Function.calcList(width))
    result.append(Basic_Function.calcList(ratio))
    return result


def process(img):
    binary = Basic_Function.binarization(img)
    # binary = cv.bitwise_not(binary)
    binary = Basic_Function.open(binary)
    # cv.imwrite("RiceBinary2.png", binary)
    result = calc(img, binary)
    return img, result


start = time.time()
# source_path = '/home/pi/Documents/ipheno/static/grain.png'
source_path = 'D:\\Project\\PythonProjects\\ipheno\\static\\grain.png'
# path = '/home/pi/Documents/ipheno/static/grain_result.png'
path = 'D:\\Project\\PythonProjects\\ipheno\\static\\grain_result.png'
result_path = '/home/pi/Documents/ipheno/algorithm/results/grain_result.json'
img = cv.imread(source_path)  # 读入图片
h, w, s = img.shape
logging.debug('h: ' + str(h) + ' , w: ' + str(w))
img2 = img[550:2600, 650:3600]
IMG, result = process(img2)

'''
2880 3840
IMG为结果标记图片，蓝色轮廓为独立谷粒，红色轮廓为粘连谷粒，黑色矩形为谷粒的最小外接矩形

result依次包含谷粒数量、谷粒长轴参数（最大值、最小值、平均值、方差、标准差、极差、中位数）、
谷粒短轴参数（最大值、最小值、平均值、方差、标准差、极差、中位数）、谷粒长宽比参数（最大值、最小值、平均值、方差、标准差、极差、中位数）

提取具体参数的方法，例如需要谷粒长轴长度的平均值则为：result[1][2]
'''
cv.imwrite(path, IMG)
if result == 0:
    logging.error("Error!")
else:
    # for r in result:
    #     logging.info(r)
    for i in range(1, 3):
        for j in range(7):
            result[i][j] = round(result[i][j] / 10, 3)
    for i in range(7):
        result[3][i] = round(result[3][i], 3)
    # print(result)
    para_results = {
        '穗长': 'NONE',
        '一次支梗数': 'NONE',
        '总粒数': str(result[0]),
        '千粒重': 'NONE',
        '节间长度最大值': 'NONE',
        '节间长度最小值': 'NONE',
        '节间长度平均值': 'NONE',
        '节间长度方差': 'NONE',
        '节间长度标准差': 'NONE',
        '节间长度极差': 'NONE',
        '节间长度中位数': 'NONE',
        '粒长度最大值': str(result[1][0]) + ' mm',
        '粒长度最小值': str(result[1][1]) + ' mm',
        '粒长度平均值': str(result[1][2]) + ' mm',
        '粒长度方差': str(result[1][3]),
        '粒长度标准差': str(result[1][4]) + ' mm',
        '粒长度极差': str(result[1][5]) + ' mm',
        '粒长度中位数': str(result[1][6]) + ' mm',
        '粒宽度最大值': str(result[2][0]) + ' mm',
        '粒宽度最小值': str(result[2][1]) + ' mm',
        '粒宽度平均值': str(result[2][2]) + ' mm',
        '粒宽度方差': str(result[2][3]),
        '粒宽度标准差': str(result[2][4]) + ' mm',
        '粒宽度极差': str(result[2][5]) + ' mm',
        '粒宽度中位数': str(result[2][6]) + ' mm',
        '粒长宽比最大值': str(result[3][0]),
        '粒长宽比最小值': str(result[3][1]),
        '粒长宽比平均值': str(result[3][2]),
        '粒长宽比方差': str(result[3][3]),
        '粒长宽比标准差': str(result[3][4]),
        '粒长宽比极差': str(result[3][5]),
        '粒长宽比中位数': str(result[3][6]),
        '实粒数': 'NONE',
        '瘪粒数': 'NONE',
        '结实率': 'NONE',
        '实粒质量': 'NONE',
        '颜色等级': 'NONE',
        '茎叶夹角': 'NONE',
        '剑叶面积': 'NONE',
        '剑叶直线度': 'NONE',
        '剑叶长度': 'NONE',
        '剑叶宽度': 'NONE',
        '剑叶长宽比': 'NONE',
        '剑叶颜色等级': 'NONE',
        '直弯穗': 'NONE',
        '松紧穗': 'NONE',
        '投影面积': 'NONE',
        '株高': 'NONE',
        '株宽': 'NONE',
        '分蘖数': 'NONE',
        '侧面面积': 'NONE',
    }
    print(para_results)
    try:
        with open(result_path, 'w', encoding='UTF-8') as j_f:
            j_f.write(json.dumps(para_results))
    except IOError as ioerr:
        print("文件 %s 无法创建" % result_path)
logging.info("程序总用时：" + str(time.time() - start))

# C:\Users\93715\python
# encoding: utf-8
"""
@author: LiuZhe
@license: (C) Copyright SJTU ME
@contact: LiuZhe_54677@sjtu.edu.cn
@file: results.py
@time: 2020/5/18 17:50
@desc:
"""


# the results from the algorithm
# TODO: 储存算法的结果包括 51参数和图片
#       主要问题：
class Results:
    def __init__(self):
        self.img_parameters = {
            '品种号': 'NONE',
            '穗长': 'NONE',
            '一次支梗数': 'NONE',
            '总粒数': 'NONE',
            '千粒重': 'NONE',
            '节间长度最大值': 'NONE',
            '节间长度最小值': 'NONE',
            '节间长度平均值': 'NONE',
            '节间长度方差': 'NONE',
            '节间长度标准差': 'NONE',
            '节间长度极差': 'NONE',
            '节间长度中位数': 'NONE',
            '粒长度最大值': 'NONE',
            '粒长度最小值': 'NONE',
            '粒长度平均值': 'NONE',
            '粒长度方差': 'NONE',
            '粒长度标准差': 'NONE',
            '粒长度极差': 'NONE',
            '粒长度中位数': 'NONE',
            '粒宽度最大值': 'NONE',
            '粒宽度最小值': 'NONE',
            '粒宽度平均值': 'NONE',
            '粒宽度方差': 'NONE',
            '粒宽度标准差': 'NONE',
            '粒宽度极差': 'NONE',
            '粒宽度中位数': 'NONE',
            '粒长宽比最大值': 'NONE',
            '粒长宽比最小值': 'NONE',
            '粒长宽比平均值': 'NONE',
            '粒长宽比方差': 'NONE',
            '粒长宽比标准差': 'NONE',
            '粒长宽比极差': 'NONE',
            '粒长宽比中位数': 'NONE',
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
        self.img_info = {
            'imageName': 'NONE',
            'image': 'NONE',
            # 'update': False
        }

    def get_image_parameters(self):
        """
        :return: Image's 51 parameters
        """
        return self.img_parameters.copy()

    def get_image_info(self):
        """
        :return: Image's information:name and the result of image
        """
        return self.img_info.copy()

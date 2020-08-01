import cv2 as cv
import panicle_al
import time

if __name__ == '__main__':
    start = time.time()
    initial = cv.imread(r"../source/panicle.jpg")
    result, thin_IMG, prim_IMG, first_IMG = panicle_al.process(initial)
    end = time.time()
    print("CostTime:", end - start)
    # print("CostTime2:", end2 - start2)
    print("Over, the following is the result:")
    for r in result:
        print(r)
    '''
    result一次包含：穗轴长度、一次枝梗数、节间长度参数[最大值、最小值、平均值、方差、标准差、极差、中位数]、投影面积、株高、株宽
    thin_IMG为骨架细化图
    prim_IMG为穗轴标记图
    first_IMG为一直枝梗标记图
    '''
    print('thin_img', thin_IMG)
import numpy as np
import cv2 as cv
import math
import Basic_Function
from numba import jit
import time


class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y


IMG = [0] * 9
temp_num = [0] * 256
tem_adj = [Point(8, 8)] * 1024
for num in range(256):
    IMG[8] = num & 1
    IMG[7] = num >> 1 & 1
    IMG[6] = num >> 2 & 1
    IMG[5] = num >> 3 & 1
    IMG[4] = 1
    IMG[3] = num >> 4 & 1
    IMG[2] = num >> 5 & 1
    IMG[1] = num >> 6 & 1
    IMG[0] = num >> 7 & 1
    size = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if IMG[j + 1 + (i + 1) * 3] > 0 and (i != 0 or j != 0):
                if abs(i) == 1 and abs(j) == 1 and (IMG[j + 1 + (0 + 1) * 3] > 0 or IMG[0 + 1 + (i + 1) * 3] > 0):
                    continue
                else:
                    tem_adj[num * 4 + size] = Point(j, i)
                    size += 1
    temp_num[num] = size


class Edge():
    def __init__(self):
        self.headNode = 0
        self.tailNode = 0
        self.head = Point(0, 0)
        self.tail = Point(0, 0)
        self.linePoints = []


class Vertex():
    def __init__(self):
        self.nPoint = Point(0, 0)
        self.adjEdges = []
        self.index = 0
        self.adjnum = 0


class BezierLine():
    def __init__(self):
        self.bezier_inter_points = []
        self.node_points = []
        self.length_node_to_node = []
        self.total_length = 0


@jit()
def fastThin(binary):
    array = [0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, \
             1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, \
             0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, \
             1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, \
             1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
             1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, \
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
             0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, \
             1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, \
             0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, \
             1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, \
             1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
             1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, \
             1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, \
             1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0]

    check = True
    thin = binary.astype(np.float32)
    h, w = thin.shape
    # print([h, w])
    round = 0
    num1 = num2 = 10

    while check == True and round < 50 and (num1 > 1 or num2 > 1):
        num1 = 0
        num2 = 0
        NEXT = 1
        check = False
        for i in range(h):
            for j in range(w):
                if NEXT == 0:
                    NEXT = 1
                else:
                    M = thin[i, j - 1] + thin[i, j] + thin[i, j + 1] if 0 < j < w - 1 else 1
                    if thin[i, j] == 0 and M != 0:
                        a = [0] * 9
                        for k in range(3):
                            for l in range(3):
                                if -1 < (i - 1 + k) < h and -1 < (j - 1 + l) < w and thin[i - 1 + k, j - 1 + l] == 255:
                                    a[k * 3 + l] = 1
                        sum = a[0] * 1 + a[1] * 2 + a[2] * 4 + a[3] * 8 + a[5] * 16 + a[6] * 32 + a[7] * 64 + a[8] * 128
                        thin[i, j] = array[sum] * 255
                        if array[sum] == 1:
                            num1 = num1 + 1
                            NEXT = 0
                            check = True

        NEXT = 1
        # print(num1)
        for j in range(w):
            for i in range(h):
                if NEXT == 0:
                    NEXT = 1
                else:
                    M = thin[i - 1, j] + thin[i, j] + thin[i + 1, j] if 0 < i < h - 1 else 1
                    if thin[i, j] == 0 and M != 0:
                        a = [0] * 9
                        for k in range(3):
                            for l in range(3):
                                if -1 < (i - 1 + k) < h and -1 < (j - 1 + l) < w and thin[i - 1 + k, j - 1 + l] == 255:
                                    a[k * 3 + l] = 1
                        sum = a[0] * 1 + a[1] * 2 + a[2] * 4 + a[3] * 8 + a[5] * 16 + a[6] * 32 + a[7] * 64 + a[8] * 128
                        thin[i, j] = array[sum] * 255
                        if array[sum] == 1:
                            num2 = num2 + 1
                            NEXT = 0
                            check = True
        # print(num2)
        # print(check)
        round = round + 1
    thin = thin.astype(np.uint8)

    return thin


def distance(a, b):
    s = (a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y)
    d = np.sqrt(s)
    return d


def adjEdgeNumber(img, x, y):
    if img[x, y] > 0:
        return 0
    n = 0
    if img[x - 1, y - 1] == 0:
        n = n + 128
    if img[x - 1, y] == 0:
        n = n + 64
    if img[x - 1, y + 1] == 0:
        n = n + 32
    if img[x, y - 1] == 0:
        n = n + 16
    if img[x, y + 1] == 0:
        n = n + 8
    if img[x + 1, y - 1] == 0:
        n = n + 4
    if img[x + 1, y] == 0:
        n = n + 2
    if img[x + 1, y + 1] == 0:
        n = n + 1
    return temp_num[n]


def adjPoints(img, p):
    y = p.x
    x = p.y
    pts = []
    if img[x, y] > 0:
        return pts
    n = 0
    if img[x - 1, y - 1] == 0:
        n = n + 128
    if img[x - 1, y] == 0:
        n = n + 64
    if img[x - 1, y + 1] == 0:
        n = n + 32
    if img[x, y - 1] == 0:
        n = n + 16
    if img[x, y + 1] == 0:
        n = n + 8
    if img[x + 1, y - 1] == 0:
        n = n + 4
    if img[x + 1, y] == 0:
        n = n + 2
    if img[x + 1, y + 1] == 0:
        n = n + 1
    for i in range(temp_num[n]):
        u = Point(tem_adj[n * 4 + i].x + y, tem_adj[n * 4 + i].y + x)
        pts.append(u)
    return pts


def getAdjEdge(pre1, cur1, img):
    pts = []
    cur = Point(cur1.x, cur1.y)
    pre = Point(pre1.x, pre1.y)
    _adjPTs = adjPoints(img, cur)
    num = adjEdgeNumber(img, cur.y, cur.x)
    pts.append(Point(cur.x, cur.y))
    while num == 2:
        if pre.y == _adjPTs[0].y and pre.x == _adjPTs[0].x:
            pre.y = cur.y
            pre.x = cur.x
            cur.y = _adjPTs[1].y
            cur.x = _adjPTs[1].x
        else:
            pre.y = cur.y
            pre.x = cur.x
            cur.y = _adjPTs[0].y
            cur.x = _adjPTs[0].x

        _adjPTs = adjPoints(img, cur)
        num = adjEdgeNumber(img, cur.y, cur.x)
        pts.append(Point(cur.x, cur.y))
    return pts


def creatGraph(img, src):
    start = time.time()
    img2 = np.copy(img)
    height, width = img.shape
    index = 0
    G = []
    point = []
    img = np.array(img)
    for i in range(height):
        for j in range(width):
            if img[i, j] > 0:
                continue
            _adj_n = adjEdgeNumber(img, i, j)
            if _adj_n > 0 and _adj_n != 2:
                if _adj_n == 1:
                    cv.circle(img2, (j, i), 5, (0, 0, 0), -1)
                cv.circle(src, (j, i), 5, (0, 0, 0), -1)
                V = Vertex()
                V.nPoint = Point(j, i)
                V.index = index
                V.adjnum = _adj_n
                G.append(V)
                index += 1
                point.append((j, i))
    l = len(G)
    for k in range(l):
        s = G[k].nPoint
        _adjPTs = adjPoints(img, s)
        for p in _adjPTs:
            linePTs = getAdjEdge(G[k].nPoint, p, img)
            edge = Edge()
            edge.tailNode = k
            if len(linePTs) != 0:
                edge.headNode = point.index((linePTs[-1].x, linePTs[-1].y))
                linePTs.pop()
            edge.tail.x = G[edge.tailNode].nPoint.x
            edge.tail.y = G[edge.tailNode].nPoint.y
            edge.head.x = G[edge.headNode].nPoint.x
            edge.head.y = G[edge.headNode].nPoint.y
            edge.linePoints = linePTs
            G[k].adjEdges.append(edge)
    end = time.time()
    # print("CG: ",end-start)
    return G


def delete_Edge(E, G, img, src):
    k = 0
    for p in E.linePoints:
        img[p.y, p.x] = 255
        k += 1
    Vtail = G[E.tailNode]
    Vhead = G[E.headNode]

    if Vhead.adjnum == 1:
        img[Vhead.nPoint.y, Vhead.nPoint.x] = 255
        # print('delte head',[Vhead.nPoint.y,Vhead.nPoint.x])
        cv.circle(img, (Vhead.nPoint.x, Vhead.nPoint.y), 3, (0, 0, 0), -1)
        k += 1
    if Vtail.adjnum == 1:
        img[Vtail.nPoint.y, Vtail.nPoint.x] = 255
        # print('delte tail', [Vtail.nPoint.y,Vtail.nPoint.x])
        k += 1


def delete_shortleaf(G, img, minlineLength, src):
    h, w = img.shape
    lowest_node = -1
    midBottom = Point(w / 2, h)  # 图像坐标下
    minDist_toMidBottom = h + w
    for v in G:
        if v.adjnum == 1:
            if distance(v.nPoint, midBottom) < minDist_toMidBottom:
                lowest_node = v.index
                minDist_toMidBottom = distance(v.nPoint, midBottom)
    for v in G:
        if v.adjnum == 1 and v.index != lowest_node:
            e = v.adjEdges
            E = e[0]
            if len(E.linePoints) < minlineLength:
                delete_Edge(E, G, img, src)
    G.clear()
    G = creatGraph(img, src)
    return G, img


def calcLineLength(pts):
    a = len(pts)
    length = 0
    if a == 0:
        return 0
    else:
        for i in range(a - 1):
            length += distance(pts[i], pts[i + 1])
        return length


def dfsTree(G, V_id, isVisited):
    if isVisited[V_id] == True:
        return 0
    pionts_num = 1
    isVisited[V_id] = True
    if G[V_id].adjnum == 0:
        return pionts_num
    for itr in G[V_id].adjEdges:
        pionts_num += len(itr.linePoints) + dfsTree(G, itr.headNode, isVisited)

    return pionts_num


def dfsPrimaryPath(G, path, result, isVisited):
    isVisited[path[-1]] = True
    check = True
    while check == True:
        check = False
        list_Edge = G[path[-1]].adjEdges
        min = 360
        path.append(10)
        for E in list_Edge:
            if isVisited[E.headNode] == False:
                isVisited[E.headNode] = True
                if G[E.headNode].adjnum == 1:
                    continue
                deg = math.atan2(E.tail.y - E.head.y, E.tail.x - E.head.x)
                deg = np.abs(math.pi / 2 - deg) * 180 / math.pi
                # print("DEG:",deg)
                if deg < min:
                    min = deg
                    path.pop()
                    path.append(E.headNode)
                check = True
    path.pop()
    list_Edge = G[path[-1]].adjEdges
    minDEG = 180
    lastNode = path[-1]
    for E in list_Edge:
        deg = math.atan2(E.tail.y - E.head.y, E.tail.x - E.head.x)
        deg = np.abs(math.pi / 2 - deg) * 180 / math.pi
        if deg < minDEG:
            minDEG = deg
            lastNode = E.headNode
    path.append(lastNode)
    if G[result[-1]].nPoint.y > G[path[-1]].nPoint.y:
        result.clear()
        for x in path:
            result.append(x)


def drawprim(G, thin1, list):
    thin = thin1.copy()
    l = 0
    dis = []
    for node in list:
        cv.circle(thin, (G[node].nPoint.x, G[node].nPoint.y), 5, (0, 0, 0), -1)
        list_edges = G[node].adjEdges
        for E in list_edges:
            if E.headNode in list:
                temp = calcLineLength(E.linePoints)
                if temp > 3:
                    dis.append(temp)
                l = temp + l
                for p in E.linePoints:
                    cv.circle(thin, (p.x, p.y), 3, (0, 0, 0), -1)
    return thin, l, dis


def dfsLongestPath(G, path, pathLength, result, maxLength, isVisited):
    isVisited = True
    list_Edge = G[path[-1]].adjEdges
    for E in list_Edge:
        edge_length = calcLineLength(E.linePoints)
        path.append(E.headNode)
        dfsLongestPath(G, path, pathLength + edge_length, result, maxLength, isVisited)
        path.pop()
    if pathLength > maxLength:
        maxLength = pathLength
        result.clear()
        for x in path:
            result.append(x)


def drawTree(V, Thin):
    Thin[V.nPoint.y, V.nPoint.x] = 0
    for edge in V.adjEdges:
        for p in edge.linePoints:
            Thin[p.y, p.x] = 0


def setToMaxConnectGraph(G, Thin, src):
    isVisited = [False] * len(G)
    max_graph_first_id = -1
    max_points_num = 0
    Thin = np.array(Thin)
    for i in range(len(G)):
        if isVisited[i] == False:
            graph_points_num = dfsTree(G, i, isVisited)
            if max_points_num < graph_points_num:
                max_points_num = graph_points_num
                max_graph_first_id = i
    h, w = Thin.shape
    for i in range(h):
        for j in range(w):
            Thin[i, j] = 255
    if max_graph_first_id == -1:
        G.clear()
        return
    isVisited = [False] * len(G)
    dfsTree(G, max_graph_first_id, isVisited)
    for i in range(len(G)):
        if isVisited[i] == True:
            drawTree(G[i], Thin)
    G.clear()
    G = creatGraph(Thin, src)
    return G, Thin


def findPrimaryPath(G, Thin):
    length = 0
    lengthlist = []
    min_dist = 1000000007
    min_dist_notLeaf = 1000000007
    primNodeList = []
    firstNodeId = -1
    firstNodeId_notLeaf = -1
    midBotton = Vertex()
    h, w = Thin.shape
    midBotton.nPoint = Point(w / 2, h)
    Thin = np.array(Thin)
    for id in range(len(G)):
        d = distance(midBotton.nPoint, G[id].nPoint)
        if G[id].adjnum == 1 and d < min_dist:
            min_dist = d
            firstNodeId = id
        if G[id].adjnum == 1 and d < min_dist_notLeaf:
            min_dist_notLeaf = d
            firstNodeId_notLeaf = id
    # print([firstNodeId, firstNodeId_notLeaf])
    if firstNodeId == -1 and firstNodeId_notLeaf == -1:
        return primNodeList
    elif firstNodeId_notLeaf > -1:
        firstNodeId = firstNodeId_notLeaf
    isVisited = [False] * len(G)
    path = []
    path.append(firstNodeId)
    primNodeList.append(firstNodeId)
    dfsPrimaryPath(G, path, primNodeList, isVisited)
    return primNodeList


def calcFirstBranch(G, list, thin):
    thin2 = thin.copy()
    num = 0
    for v in G:
        if v.adjnum == 1:
            for e in v.adjEdges:
                if (e.headNode in list) and (e.tailNode not in list):
                    num += 1
                    for p in e.linePoints:
                        cv.circle(thin2, (p.x, p.y), 3, (0, 0, 0), -1)
    return num, thin2


def calcList(list):
    max, min = Basic_Function.max_and_min(list)
    aver = Basic_Function.aver(list)
    dev, sdev = Basic_Function.dev_and_sdev(list, aver)
    vp, median = Basic_Function.vp_and_median(list)
    return [max, min, aver, dev, sdev, vp, median]


def calcArea(img):
    area = 0
    h, w = img.shape
    for i in range(h):
        for j in range(w):
            if img[i, j] == 0:
                area += 1
    return area


def calcHeightandWidth(thin):
    max_X = 0
    min_X = 10000
    max_Y = 0
    min_Y = 10000
    h, w = thin.shape
    for i in range(h):
        for j in range(w):
            if thin[i, j] == 0:
                if j < min_X:
                    min_X = j
                if j > max_X:
                    max_X = j
                if i < min_Y:
                    min_Y = i
                if i > max_Y:
                    max_Y = i
    height = max_Y - min_Y
    width = max_X - min_X
    return height, width


def fillhole(Thin, area, src):
    Thin = cv.bitwise_not(Thin)
    # cv.imwrite("instead.png", Thin)
    contours, hierarchy = cv.findContours(Thin.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cv.drawContours(src, contours, -1, (0, 0, 255), 2)
    for i in range(len(contours)):
        if hierarchy[0][i][3] != -1:
            if cv.contourArea(contours[i]) < area:
                cv.drawContours(Thin, contours, i, (255, 255, 255), -1)
            else:
                if cv.contourArea(contours[i]) < area:
                    cv.drawContours(Thin, contours, i, (0, 0, 0), -1)
                # else:
                # cv.drawContours(src,contours,i,(255,0,0),2)
    Thin = cv.bitwise_not(Thin)
    return Thin


def process(img):
    result = []
    img = cv.resize(img, (1024, 1532))
    binary = Basic_Function.binarization(img)  # 二值化
    Area = calcArea(binary)  # 计算投影面积
    binary = fillhole(binary, 3000, img)
    # cv.imwrite("contour.png", img)
    # binary = Basic_Function.open(binary) #开运算
    # cv.imwrite("8-Binary.png", binary)
    start = time.time()
    thin = fastThin(binary)  # 快速细化
    end = time.time()
    # print("FT: ", end - start)
    G = creatGraph(thin, img)  # 建图
    G, thin2 = setToMaxConnectGraph(G, thin, img)  # 最大连通域
    # cv.imwrite("8-Thin.png", thin)
    G, thin3 = delete_shortleaf(G, thin2, 60, img)  # 剔除较短杂枝
    height, width = calcHeightandWidth(thin3)
    primaryNodeList = findPrimaryPath(G, thin3)  # 获得主轴节点序列
    prim_IMG, mainLength, Dis_bt_InnerNodes = drawprim(G, thin3, primaryNodeList)  # 主轴标记图和主轴长度、节间长度列表
    # cv.imwrite("8-Primary.png", prim_IMG)
    result.append(mainLength)
    num_FirstBranch, first_IMG = calcFirstBranch(G, primaryNodeList, thin2)  # 计算一次枝梗数目，获得一次枝梗标记图
    # cv.imwrite("8-FirstBranch.png", first_IMG)
    result.append(num_FirstBranch)
    list_parameter = calcList(Dis_bt_InnerNodes)
    result.append(list_parameter)
    result.append(Area)
    result.append(height)
    result.append(width)
    '''
    result一次包含：穗轴长度、一次枝梗数、节间长度参数[最大值、最小值、平均值、方差、标准差、极差、中位数]、投影面积、株高、株宽
    '''
    return result, thin3, prim_IMG, first_IMG

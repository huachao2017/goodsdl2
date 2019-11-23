import matplotlib.pyplot as plt

# 添加这段代码的目的是让图片中的中文能够正常显示！
from pylab import *

mpl.rcParams['font.sans-serif'] = ['SimHei']


def test_plot_tree():

    # 程序清单3-6：获取叶节点的数目
    def getNumLeafs(myTree):
        numLeafs = 0  # 初始化叶子
        firstStr = list(myTree.keys())[0]  # 获取结点属性,第一个关键字，第一次划分数据集的类别标签
        secondDict = myTree[firstStr]  # 获取下一组字典
        # 从根节点开始遍历
        for key in secondDict.keys():
            if type(secondDict[key]).__name__ == 'dict':
                # 测试该结点是否为字典，如果不是字典，代表此结点为叶子结点
                numLeafs += getNumLeafs(secondDict[key])  # 递归调用
            else:
                numLeafs += 1
        return numLeafs

    # 程序清单3-6：获取树的层数
    def getTreeDepth(myTree):
        maxDepth = 0  # 初始化决策树深度
        firstStr = list(myTree.keys())[0]  # 获取结点属性
        secondDict = myTree[firstStr]  # 获取下一组字典
        # 根节点开始遍历
        for key in secondDict.keys():
            # 判断节点的个数，终止条件是叶子节点
            if type(secondDict[key]).__name__ == 'dict':
                # 测试该结点是否为字典，如果不是字典，代表此结点为叶子结点
                thisDepth = 1 + getTreeDepth(secondDict[key])
            else:
                thisDepth = 1
            if thisDepth > maxDepth:
                maxDepth = thisDepth
                # 更新层数
        return maxDepth

    # 测试数据集，输出存储的树信息
    def retrieveTree(i):
        listOfTrees = [{'no surfacing': {0: 'no', 1: {'flippers': {0: 'no', 1: 'yes'}}}},
                       {'no surfacing': {0: 'no', 1: {'flippers': {0: {'head': {0: 'no', 1: 'yes'}}, 1: 'no'}}}}
                       ]
        return listOfTrees[i]

    def plotMidText(cntrPt, parentPt, txtString):
        # 在父子节点间填充文本信息
        xMid = (parentPt[0] - cntrPt[0]) / 2.0 + cntrPt[0]
        yMid = (parentPt[1] - cntrPt[1]) / 2.0 + cntrPt[1]
        # createPlot.ax1.text(xMid, yMid, txtString)
        createPlot.ax1.text(xMid, yMid, txtString, va="center", ha="center", rotation=30)

    def plotTree(myTree, parentPt, nodeTxt):
        # 计算宽与高
        numLeafs = getNumLeafs(myTree)
        defth = getTreeDepth(myTree)
        firstStr = list(myTree.keys())[0]
        # 找到第一个中心点的位置，然后与parentPt定点进行划线
        cntrPt = (plotTree.xOff + (1.0 + float(numLeafs)) / 2.0 / plotTree.totalW, plotTree.yOff)  # 中心位置
        # 打印输入对应的文字
        plotMidText(cntrPt, parentPt, nodeTxt)
        # 可视化Node分支点
        plotNode(firstStr, cntrPt, parentPt, decisionNode)
        secondeDict = myTree[firstStr]  # 下一个字典
        # 减少y的偏移，按比例减少 ，y值 = 最高点 - 层数的高度[第二个节点位置]
        plotTree.yOff = plotTree.yOff - 1.0 / plotTree.totalD
        for key in secondeDict.keys():
            # 这些节点既可以是叶子结点也可以是判断节点
            # 判断该节点是否是Node节点
            if type(secondeDict[key]) is dict:
                # 如果是就递归调用
                plotTree(secondeDict[key], cntrPt, str(key))
            else:
                # 如果不是，就在原来节点一半的地方找到节点的坐标
                plotTree.xOff = plotTree.xOff + 1.0 / plotTree.totalW
                # 可视化该节点的位置
                plotNode(secondeDict[key], (plotTree.xOff, plotTree.yOff), cntrPt, leafNode)
                # 并打印输入对应的文字
                plotMidText((plotTree.xOff, plotTree.yOff), cntrPt, str(key))
        plotTree.yOff = plotTree.yOff + 1.0 / plotTree.totalD

    # 创建绘图区，计算树形图的全局尺寸
    def createPlot(inTree):
        fig = plt.figure(1, facecolor='white')
        # 清空当前图像窗口
        fig.clf()
        axprops = dict(xticks=[], yticks=[])
        createPlot.ax1 = plt.subplot(111, frameon=False, **axprops)
        # 存储树的宽度
        plotTree.totalW = float(getNumLeafs(inTree))
        # 存储树的深度
        plotTree.totalD = float(getTreeDepth(inTree))
        # 追踪已经绘制的节点位置，以及放置下个节点的恰当位置
        plotTree.xOff = -0.5 / plotTree.totalW
        plotTree.yOff = 1.0
        plotTree(inTree, (0.5, 1.0), '')
        plt.savefig('./test2.jpg')
        # plt.show()

    # 绘制带箭头的注解
    def plotNode(nodeTxt, centerPt, parentPt, nodeType):
        createPlot.ax1.annotate(nodeTxt, xy=parentPt, xycoords='axes fraction', xytext=centerPt,
                                textcoords='axes fraction', va="center", ha="center", bbox=nodeType,
                                arrowprops=arrow_args)

    # 定义文本框和箭头格式，sawtooth 波浪方框， round4矩形方框， fc表示字体颜色的深浅 0.1~0.9依次变浅
    decisionNode = dict(boxstyle="sawtooth", fc="0.8")
    leafNode = dict(boxstyle="round4", fc="0.8")
    arrow_args = dict(arrowstyle="<-")

    myTree = retrieveTree(0)
    createPlot(myTree)


if __name__ == "__main__":
    test_plot_tree()

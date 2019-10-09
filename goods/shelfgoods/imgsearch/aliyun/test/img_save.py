import os
import cv2
def test_acc():
    jpgpath = "D:\\opt\\data\\goods\\upc_test\\"
    savepath = "D:\\opt\\data\\goods\\upc_test1\\"
    upc_files = os.listdir(jpgpath)
    j = 0
    i = 0
    for file in upc_files:
        upc_f = str(file).split("_")[0]
        filepath = os.path.join(jpgpath,file)
        img = cv2.imread(filepath)
        img = cv2.resize(img, (200, 200))
        path = os.path.join(savepath,file)
        cv2.imwrite(path,img)

if __name__=='__main__':
    test_acc()
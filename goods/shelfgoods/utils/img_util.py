import cv2
import numpy as np
import matplotlib.pyplot as plt

def perspective(img,xmin,ymin,xmax,ymax):
    H_rows, W_cols= img.shape[:2]
    print(H_rows, W_cols)
    # 原图中书本的四个角点(左上、右上、左下、右下),与变换后矩阵位置
    pts1 = np.float32([[xmin, ymin], [xmax, ymin], [xmin, ymax], [xmax, ymax]])
    pts2 = np.float32([[0, 0],[W_cols,0],[0, H_rows],[H_rows,W_cols],])
    # 生成透视变换矩阵；进行透视变换
    M = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(img, M, (H_rows+5,W_cols+5))
    return dst

if __name__=="__main__":
    img = cv2.imread('original_img.jpg')

    perspective(img)
    cv2.imshow("original_img", img)
    cv2.imshow("result", dst)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
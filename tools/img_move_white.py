import os
import cv2
import numpy as np

if __name__ == "__main__":

    dir = 'c:/fastxbox/data/img'
    output_dir = 'c:/fastxbox/data/solve_img'
    for name in os.listdir(dir):
        img_path = os.path.join(dir, name)
        if os.path.isfile(img_path):
            print(img_path)
            save_img_path = os.path.join(output_dir, '{}.jpg'.format(name))
            try:
                img = cv2.imread(img_path)
                img_16 = img.astype(np.int16)
                img_one_channel = img_16[:,:,0] + img_16[:,:,1] + img_16[:,:,2]
                (x,y) = np.where(img_one_channel<765)
                min_x = np.min(x)
                min_y = np.min(y)
                max_x = np.max(x)
                max_y = np.max(y)
                target_img = img[int(min_x):int(max_x), int(min_y):int(max_y)]
                cv2.imwrite(save_img_path, target_img)
            except Exception as e:
                print(e)

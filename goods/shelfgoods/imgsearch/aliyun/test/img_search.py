import os
from goods.shelfgoods.imgsearch.aliyun.search import ImgSearch
imgs_file_path = "D:\\opt\\data\\goods\\uc_merchant_goods\\img\\"
import time
def add_img():
    files = os.listdir(imgs_file_path)
    search_ins = ImgSearch()
    for file in files:
        upc = str(file).strip(".jpg").split("_")[0]
        img_name = str(file).strip(".jpg")
        img_path = os.path.join(imgs_file_path,file)
        print (img_path)
        #D:\opt\data\goods\uc_merchant_goods\img\11001126_686.jpg
        try:
            code = search_ins.add_img(upc,img_name,img_path)
            if code == 0:
                print ("success")
            # time.sleep(0.2)
            break
        except:
            print ("error:"+str(img_path))

def search_img():
    search_ins = ImgSearch()
    imgpath = "D:\\opt\\data\\11\\2.png"
    upc = search_ins.search_img(imgpath)
    print (upc)

def delete_img():
    search_ins = ImgSearch()
    code = search_ins.delete_img('11001126')
    if code == 0:
        print (code)

def test_acc():
    search_ins = ImgSearch()
    jpgpath = "D:\\opt\\data\\goods\\upc_test\\"
    upc_files = os.listdir(jpgpath)
    j = 0
    i = 0
    for file in upc_files:
        upc_f = str(file).split("_")[0]
        filepath = os.path.join(jpgpath,file)
        upc = search_ins.search_img(filepath)
        time.sleep(1)
        j+=1
        if upc!=None and upc == upc_f:
            i+=1
    print (float(i/j))

if __name__=='__main__':
    # add_img()
    # search_img()
    # delete_img()
    test_acc()
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
def add_img1():
    search_ins = ImgSearch()
    img_path = "D:\\opt\\data\\goods\\upc_test2\\"
    img_files = ["6902538005141_40713.jpg","6902538006261_32622.jpg","6903252000771_32273.jpg","6920180209724_37530.jpg","6921168593552_33638.jpg","6924743915770_32631.jpg"]
    for file in img_files:
        img_name = file.strip(".jpg")
        upc = file.split("_")[0]
        code = search_ins.add_img(upc,img_name,img_path+file)
        print (code)
        time.sleep(0.5)

def search_img():
    search_ins = ImgSearch()
    imgpath = "D:\\opt\\data\\11\\3.png"
    upc = search_ins.search_img(imgpath)
    print (upc)

def delete_img():
    search_ins = ImgSearch()
    upcs = ['6902538005141','6902538006261','6903252000771','6920180209724','6921168593552','6924743915770']
    for upc in upcs:
        code = search_ins.delete_img(upc)
        time.sleep(1)
        if code == 0:
            print (code)

def test_acc():
    search_ins = ImgSearch()
    jpgpath = "D:\\opt\\data\\goods\\upc_test2\\"
    upc_files = os.listdir(jpgpath)
    j = 0
    i = 0
    k = 0
    l= 0
    for file in upc_files:
        upc_f = str(file).split("_")[0]
        print (upc_f)
        filepath = os.path.join(jpgpath,file)
        upcs = search_ins.search_img(filepath)
        # time.sleep(0.5)
        j+=1
        if upcs!=None and upc_f in upcs:
            i+=1
        if upcs!=None and len(upcs)>=1 and  upc_f not in upcs:
            k+=1
        if upcs==None or len(upcs)<1:
            l+=1

    print ("准确率："+str(float(i/j)))
    print ("错误率:"+str(float(k/j)))
    print ("未知率："+str(float(l/j)))

if __name__=='__main__':
    # add_img()
    # search_img()
    # delete_img()
    test_acc()
    # add_img1()
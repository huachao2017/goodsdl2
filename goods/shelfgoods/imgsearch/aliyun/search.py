from aliyunsdkcore.client import AcsClient
import base64
import aliyunsdkimagesearch.request.v20190325.AddImageRequest as AddImageRequest
import aliyunsdkimagesearch.request.v20190325.DeleteImageRequest as DeleteImageRequest
import aliyunsdkimagesearch.request.v20190325.SearchImageRequest as SearchImageRequest
import cv2
import logging
logger = logging.getLogger("detect")
import demjson
from set_config import config
"""
用户登录名称 hslrj@1120470512142314.onaliyun.com
登录密码 SU7yL1oDqicsAOT{Gsgo7}tIZ{oJcF?2
AccessKey ID LTAI4Ftp8inKDzFmaEWyj17P
AccessKeySecret mCVOzv0fABM19dTRlYlWMZdGlAoqsz
"""
import time
aliyun_instance = config.aliyun_instance1
class ImgSearch:
    AccessKeyID = aliyun_instance['AccessKeyID']
    AccessKeySecret = aliyun_instance['AccessKeySecret']
    region = aliyun_instance['region']
    instance_name = aliyun_instance['instance_name']
    client = None
    min_score = aliyun_instance['min_score']
    search_point = aliyun_instance['search_point']
    sleep_time = aliyun_instance['sleep_time']
    def __init__(self):
        self.client = self.get_client()
        self.client.set_max_retry_num(5)
    def get_client(self):
        client = AcsClient(self.AccessKeyID, self.AccessKeySecret, self.region)
        return client

    def add_img(self,upc,imgname,img_path):
        # 添加图片
        for i in range(1, 5):

            try:
                request = AddImageRequest.AddImageRequest()
                request.set_endpoint(self.search_point)
                request.set_InstanceName(self.instance_name)
                request.set_ProductId(upc)
                request.set_PicName(imgname)
                img = cv2.imread(img_path)
                img = cv2.resize(img, (200, 200))
                img_encode = cv2.imencode('.jpg', img)[1]
                img_encode = base64.b64encode(img_encode)
                request.set_PicContent(img_encode)
                response = self.client.do_action_with_exception(request)
                logger.info("aliyun add_img,response=" + str(response))
                code = dict(demjson.decode(response))['Code']
                return code
            except:
                time.sleep(self.sleep_time)
                continue
        return None

    def add_cvimg(self,upc,imgname,cvimg):
        # 添加图片

        for i in range(1,5):
            try:
                request = AddImageRequest.AddImageRequest()
                request.set_endpoint(self.search_point)
                request.set_InstanceName(self.instance_name)
                request.set_ProductId(upc)
                request.set_PicName(imgname)
                img = cv2.resize(cvimg, (200, 200))
                img_encode = cv2.imencode('.jpg', img)[1]
                img_encode = base64.b64encode(img_encode)
                request.set_PicContent(img_encode)
                response = self.client.do_action_with_exception(request)
                logger.info("aliyun add_img,response=" + str(response))
                code = dict(demjson.decode(response))['Code']
                return code
            except:
                time.sleep(self.sleep_time)
                continue
        return None
    #若不指定imgname 参数，则删除upc下所有图片；若指定参数，删除upc+imgname指定的图片。
    def delete_img(self,upc,imgname=None):

        for i in range(1, 5):
            try:
                request = DeleteImageRequest.DeleteImageRequest()
                request.set_endpoint(self.search_point)
                request.set_InstanceName(self.instance_name)
                request.set_ProductId(upc)
                if imgname != None:
                    request.set_PicName(imgname)
                response = self.client.do_action_with_exception(request)
                time.sleep(self.sleep_time)
                logger.info("aliyun delete_img,response=" + str(response))
                code = dict(demjson.decode(response))['Code']
                # 成功返回code == 0
                return code
            except:
                time.sleep(self.sleep_time)
                continue
        return None

    def search_img(self,img_path):
        for i in range(1,5):
            try:
                request = SearchImageRequest.SearchImageRequest()
                request.set_endpoint(self.search_point)
                request.set_InstanceName(self.instance_name)
                img = cv2.imread(img_path)
                img = cv2.resize(img, (200, 200))
                img_encode = cv2.imencode('.jpg', img)[1]
                img_encode = base64.b64encode(img_encode)
                request.set_PicContent(img_encode)
                response = self.client.do_action_with_exception(request)
                print(response)
                logger.info("aliyun search_img,response=" + str(response))
                result = dict(demjson.decode(response))
                upcs = []
                if result['Code'] == 0:
                    sort_values = list(result['Auctions'])
                    for value in sort_values:
                        ProductId = dict(value)['ProductId']
                        PicName = dict(value)['PicName']
                        SortExprValues = str(dict(value)['SortExprValues'])
                        if float(SortExprValues.split(";")[0]) > self.min_score:
                            upcs.append(ProductId)
                return upcs
            except:
                time.sleep(self.sleep_time)
                continue
        return None

    def search_cvimg(self, cvimg):
        for i in range(1, 5):
            try:
                request = SearchImageRequest.SearchImageRequest()
                request.set_endpoint(self.search_point)
                request.set_InstanceName(self.instance_name)
                img = cv2.resize(cvimg, (200, 200))
                img_encode = cv2.imencode('.jpg', img)[1]
                img_encode = base64.b64encode(img_encode)
                request.set_PicContent(img_encode)
                response = self.client.do_action_with_exception(request)
                logger.info("aliyun search_img,response=" + str(response))
                result = dict(demjson.decode(response))
                upcs = []
                if result['Code'] == 0:
                    sort_values = list(result['Auctions'])
                    for value in sort_values:
                        ProductId = dict(value)['ProductId']
                        PicName = dict(value)['PicName']
                        SortExprValues = str(dict(value)['SortExprValues'])
                        if float(SortExprValues.split(";")[0]) > self.min_score:
                            upcs.append(ProductId)
                return upcs
            except:
                time.sleep(self.sleep_time)
                continue
        return None


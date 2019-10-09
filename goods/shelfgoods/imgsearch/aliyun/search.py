from aliyunsdkcore.client import AcsClient
import base64
import aliyunsdkimagesearch.request.v20190325.AddImageRequest as AddImageRequest
import aliyunsdkimagesearch.request.v20190325.DeleteImageRequest as DeleteImageRequest
import aliyunsdkimagesearch.request.v20190325.SearchImageRequest as SearchImageRequest
import cv2
import logging
logger = logging.getLogger("detect")
import demjson
"""
用户登录名称 hslrj@1120470512142314.onaliyun.com
登录密码 SU7yL1oDqicsAOT{Gsgo7}tIZ{oJcF?2
AccessKey ID LTAI4Ftp8inKDzFmaEWyj17P
AccessKeySecret mCVOzv0fABM19dTRlYlWMZdGlAoqsz
"""
class ImgSearch:
    AccessKeyID = "LTAI4Ftp8inKDzFmaEWyj17P"
    AccessKeySecret = "mCVOzv0fABM19dTRlYlWMZdGlAoqsz"
    region = "cn-shanghai"
    instance_name = "hsimgsearch"
    client = None
    min_score = 10
    search_point = "imagesearch."+region+".aliyuncs.com"
    def __init__(self):
        self.client = self.get_client()
    def get_client(self):
        client = AcsClient(self.AccessKeyID, self.AccessKeySecret, self.region)
        return client

    def add_img(self,upc,imgname,img_path):
        # 添加图片
        try:
            request = AddImageRequest.AddImageRequest()
            request.set_endpoint(self.search_point)
            request.set_InstanceName(self.instance_name)
            request.set_ProductId(upc)
            request.set_PicName(imgname)
            img = cv2.imread(img_path)
            img = cv2.resize(img, (200,200))
            img_encode = cv2.imencode('.jpg', img)[1]
            img_encode = base64.b64encode(img_encode)
            request.set_PicContent(img_encode)
            # with open(img_path, 'rb') as imgfile:
            #     encoded_pic_content = base64.b64encode(imgfile.read())
            #     request.set_PicContent(encoded_pic_content)
            response = self.client.do_action_with_exception(request)
            logger.info("aliyun add_img,response="+str(response))
            print(response)
            code = dict(demjson.decode(response))['Code']
            return code
        except Exception as err:
            logging.error(err)
            return None

    def add_cvimg(self,upc,imgname,cvimg):
        # 添加图片
        try:
            request = AddImageRequest.AddImageRequest()
            request.set_endpoint(self.search_point)
            request.set_InstanceName(self.instance_name)
            request.set_ProductId(upc)
            request.set_PicName(imgname)
            img = cv2.resize(cvimg, (200,200))
            img_encode = cv2.imencode('.jpg', img)[1]
            img_encode = base64.b64encode(img_encode)
            request.set_PicContent(img_encode)
            # with open(img_path, 'rb') as imgfile:
            #     encoded_pic_content = base64.b64encode(imgfile.read())
            #     request.set_PicContent(encoded_pic_content)
            response = self.client.do_action_with_exception(request)
            logger.info("aliyun add_img,response="+str(response))
            print(response)
            code = dict(demjson.decode(response))['Code']
            return code
        except Exception as err:
            logging.error(err)
            return None

    def delete_img(self,upc):
        try:
            request = DeleteImageRequest.DeleteImageRequest()
            request.set_endpoint(self.search_point)
            request.set_InstanceName(self.instance_name)
            request.set_ProductId(upc)
            response = self.client.do_action_with_exception(request)
            print(response)
            logger.info("aliyun delete_img,response=" + str(response))
            code = dict(demjson.decode(response))['Code']
            # 成功返回code == 0
            return code
        except Exception as err:
            logging.error(err)
            return None

    def search_img(self,img_path):
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
            logger.info("aliyun search_img,response=" + str(response))
            result = dict(demjson.decode(response))
            if result['Code'] == 0 :
                sort_values = list(result['Auctions'])
                for value in sort_values:
                    ProductId = dict(value)['ProductId']
                    PicName = dict(value)['PicName']
                    SortExprValues = str(dict(value)['SortExprValues'])
                    if float(SortExprValues.split(";")[0]) > self.min_score:
                        return ProductId
            return None
        except Exception as err:
            logging.error(err)
            return None

    def search_cvimg(self, cvimg):
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
            if result['Code'] == 0:
                sort_values = list(result['Auctions'])
                for value in sort_values:
                    ProductId = dict(value)['ProductId']
                    PicName = dict(value)['PicName']
                    SortExprValues = str(dict(value)['SortExprValues'])
                    if float(SortExprValues.split(";")[0]) > self.min_score:
                        return ProductId
            return None
        except Exception as err:
            logging.error(err)
            return None


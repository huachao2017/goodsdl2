import base64, time, json
from urllib import request, parse
from aliyunsdkcore.client import AcsClient
import cv2
import logging

logger = logging.getLogger("detect")
from set_config import config

baidu_ai_instance = config.baidu_ai_instance1


class ImgSearch_02:
    access_token = baidu_ai_instance['access_token']
    request_url = baidu_ai_instance['request_url']
    client = None
    min_score = baidu_ai_instance['min_score']
    sleep_time = baidu_ai_instance['sleep_time']

    def __init__(self):
        self.client = self.get_client()
        self.client.set_max_retry_num(5)

    def get_client(self):
        client = AcsClient(self.access_token, self.request_url)
        return client

    def add_img(self, upc, imgname, img_path):
        try:
            with open(img_path, 'rb') as f:
                base64_data = base64.b64encode(f.read())
            brief = "{'upc':%s, 'id':%s}" % (upc, imgname)
            params = {"brief": brief, "image": base64_data}
            params = parse.urlencode(params).encode("utf-8")
            request_url = self.request_url + "add?access_token=" + self.access_token
            req = request.Request(url=request_url, data=params)
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            response = request.urlopen(req)
            str_content = response.read().decode("utf-8")
            content = json.loads(str_content)
            # print(content)
            if 'error_code' in content:
                logging.error(str_content)
                return None
            else:
                return content["cont_sign"]
        except Exception as err:
            logging.error(err)
            return None

    def add_cvimg(self, upc, imgname, cvimg):
        # 添加图片
        try:
            # cvimg = cv2.resize(cvimg, (200, 200))
            img_encode = cv2.imencode('.jpg', cvimg)[1]
            base64_data = base64.b64encode(img_encode)

            brief = "{'upc':%s, 'id':%s}" % (upc, imgname)
            params = {"brief": brief, "image": base64_data}
            params = parse.urlencode(params).encode("utf-8")
            request_url = self.request_url + "add?access_token=" + self.access_token
            req = request.Request(url=request_url, data=params)
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            response = request.urlopen(req)
            str_content = response.read().decode("utf-8")
            content = json.loads(str_content)
            if 'error_code' in content:
                logging.error(str_content)
                return None
            else:
                return content["cont_sign"]
        except Exception as err:
            logging.error(err)
            return None

    # 支持批量删除，样例："932301884,1068006219;316336521,553141152;2491030726,1352091083"
    def delete_img(self, cont_sign):
        try:
            params = {"cont_sign": cont_sign}
            params = parse.urlencode(params).encode("utf-8")
            request_url = self.request_url + "delete?access_token=" + self.access_token
            request_ = request.Request(url=request_url, data=params)
            request_.add_header('Content-Type', 'application/x-www-form-urlencoded')
            response = request.urlopen(request_)
            str_content = response.read().decode("utf-8")
            # print(str_content)
            content = json.loads(str_content)
            if 'error_code' in content:
                logging.error(str_content)
                return None
            else:
                return 0
        except Exception as err:
            logging.error(err)
            return None

    def search_img(self, img_path):
        try:
            with open(img_path, 'rb') as f:
                base64_data = base64.b64encode(f.read())

            params = {"image": base64_data}
            params = parse.urlencode(params).encode("utf-8")
            request_url = self.request_url + "search?access_token=" + self.access_token
            req = request.Request(url=request_url, data=params)
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            response = request.urlopen(req)
            content = response.read().decode("utf-8")
            # print(content)
            content = json.loads(content)
            results = content['result']
            upcs = []
            for result in results:
                score = result["score"]
                # print(score)
                if score > self.min_score:
                    a = result["brief"]
                    upcs.append(eval(result["brief"])["upc"])
                else:
                    break
            # print(upcs)
            return upcs
        except Exception as err:
            logging.error(err)
            return None

    def search_cvimg(self, cvimg):
        try:
            # cvimg = cv2.resize(cvimg, (200, 200))
            img_encode = cv2.imencode('.jpg', cvimg)[1]
            base64_data = base64.b64encode(img_encode)

            params = {"image": base64_data}
            params = parse.urlencode(params).encode("utf-8")
            request_url = self.request_url + "search?access_token=" + self.access_token
            req = request.Request(url=request_url, data=params)
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            response = request.urlopen(req)
            content = response.read().decode("utf-8")
            # print(content)
            content = json.loads(content)
            results = content['result']
            upcs = []
            for result in results:
                score = result["score"]
                if score > self.min_score:
                    upcs.append(eval(result["brief"])["upc"])
                else:
                    break
            return upcs
        except Exception as err:
            logging.error(err)
            return None


if __name__ == '__main__':
    demo = ImgSearch()
    demo.delete_img("1441064327,3222327728;1229152111,2089989172")
    # demo.search_img("/Users/fangjin/Desktop/goodsdl2/goods/shelfgoods/imgsearch/baidu_ai/test/upc_test2/6902538005141_40779.jpg")
    # demo.add_img(3567,3567_456,"/Users/fangjin/Desktop/goodsdl2/goods/shelfgoods/imgsearch/baidu_ai/test/upc_test2/6902538005141_40786.jpg")
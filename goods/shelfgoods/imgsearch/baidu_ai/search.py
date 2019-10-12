import base64, time, json
from urllib import request, parse
import cv2
import logging

logger = logging.getLogger("detect")
from set_config import config

baidu_ai_instance = config.baidu_ai_instance1


class ImgSearch_02:
    debug = baidu_ai_instance['debug']
    request_url = baidu_ai_instance['request_url']
    min_score = baidu_ai_instance['min_score']
    sleep_time = baidu_ai_instance['sleep_time']
    ak = baidu_ai_instance['ak']
    sk = baidu_ai_instance['sk']

    def add_img(self, upc, imgname, img_path):
        for i in range(1, 5):
            try:
                with open(img_path, 'rb') as f:
                    base64_data = base64.b64encode(f.read())
                brief = "{'upc':%s, 'id':%s}" % (str(upc), str(imgname))
                params = {"brief": brief, "image": base64_data}
                params = parse.urlencode(params).encode("utf-8")
                request_url = self.request_url + "add?access_token=" + self.get_token()
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
                time.sleep(self.sleep_time)
                continue
        return None

    def add_cvimg(self, upc, imgname, cvimg):
        # 添加图片

        for i in range(1, 5):
            try:
                # cvimg = cv2.resize(cvimg, (200, 200))
                img_encode = cv2.imencode('.jpg', cvimg)[1]
                base64_data = base64.b64encode(img_encode)

                brief = "{'upc':%s, 'id':%s}" % (str(upc), str(imgname))
                params = {"brief": brief, "image": base64_data}
                params = parse.urlencode(params).encode("utf-8")
                request_url = self.request_url + "add?access_token=" + self.get_token()
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
                time.sleep(self.sleep_time)
                continue
        return None

    # 支持批量删除，样例："932301884,1068006219;316336521,553141152;2491030726,1352091083"
    def delete_img(self, cont_sign):
        for i in range(1, 5):
            try:
                params = {"cont_sign": cont_sign}
                params = parse.urlencode(params).encode("utf-8")
                request_url = self.request_url + "delete?access_token=" + self.get_token()
                request_ = request.Request(url=request_url, data=params)
                request_.add_header('Content-Type', 'application/x-www-form-urlencoded')
                response = request.urlopen(request_)
                str_content = response.read().decode("utf-8")
                print(str_content)
                content = json.loads(str_content)
                if 'error_code' in content:
                    logging.error(str_content)
                    return None
                else:
                    return 0
            except Exception as err:
                logging.error(err)
                time.sleep(self.sleep_time)
                continue
        return None

    def search_img(self, img_path):
        for i in range(1, 5):
            try:
                with open(img_path, 'rb') as f:
                    base64_data = base64.b64encode(f.read())

                params = {"image": base64_data}
                params = parse.urlencode(params).encode("utf-8")
                request_url = self.request_url + "search?access_token=" + self.get_token()
                req = request.Request(url=request_url, data=params)
                req.add_header('Content-Type', 'application/x-www-form-urlencoded')
                response = request.urlopen(req)
                content = response.read().decode("utf-8")
                if self.debug:
                    print(content)
                content = json.loads(content)
                results = content['result']
                upcs = []
                for result in results:
                    score = result["score"]
                    # print(score)
                    if score > self.min_score:
                        try:
                            upcs.append(str(eval(result["brief"])["upc"]))
                        except:
                            continue
                    else:
                        break
                # print(upcs)
                return upcs
            except Exception as err:
                logging.error(err)
                time.sleep(self.sleep_time)
                continue
        return None

    def search_cvimg(self, cvimg):
        for i in range(1, 5):
            try:
                # cvimg = cv2.resize(cvimg, (200, 200))
                img_encode = cv2.imencode('.jpg', cvimg)[1]
                base64_data = base64.b64encode(img_encode)

                params = {"image": base64_data}
                params = parse.urlencode(params).encode("utf-8")
                request_url = self.request_url + "search?access_token=" + self.get_token()
                req = request.Request(url=request_url, data=params)
                req.add_header('Content-Type', 'application/x-www-form-urlencoded')
                response = request.urlopen(req)
                content = response.read().decode("utf-8")
                print(content)
                content = json.loads(content)
                results = content['result']
                upcs = []
                for result in results:
                    score = result["score"]
                    if score > self.min_score:
                        try:
                            upcs.append(str(eval(result["brief"])["upc"]))
                        except:
                            continue
                    else:
                        break
                return upcs
            except Exception as err:
                logging.error(err)
                time.sleep(self.sleep_time)
                continue
        return None

    def get_token(self):
        for i in range(1, 5):
            try:
                # client_id 为官网获取的AK， client_secret 为官网获取的SK
                host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(self.ak,self.sk)
                req = request.Request(host)
                req.add_header('Content-Type', 'application/json; charset=UTF-8')
                response = request.urlopen(req)
                content = response.read().decode("utf-8")
                content = json.loads(content)
                access_token = content["access_token"]
                print(access_token)
                return access_token
            except Exception as err:
                logging.error(err)
                time.sleep(0.1)
                continue
        return None

if __name__ == '__main__':
    demo = ImgSearch_02()

    # print(demo.add_img(100,'3567_456',"/Users/86130/Desktop/upc_test2/6902538005141_40754.jpg"))
    # print(demo.delete_img("1441064327,3222327728;1161903065,2930872941"))
    print(demo.search_img("/Users/86130/Desktop/upc_test2/6902538005141_40754.jpg"))

    # img = cv2.imread("/Users/86130/Desktop/upc_test2/6902538005141_40786.jpg")
    # print(demo.add_cvimg(100,11111,img))


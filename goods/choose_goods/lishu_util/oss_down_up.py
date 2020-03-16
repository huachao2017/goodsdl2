# -*- coding: utf-8 -*-
# api说明：https://github.com/ucloud/ufile-sdk-python
from ufile import filemanager
from io import BytesIO
from PIL import Image


class FileManager:
    """
    文件上传路径，这个项目你统一用：store_ass,
    也就是上传图片是：假如图片名是a.jpg，那么上传时名称为：store_ass/a.jpg
    """

    def __init__(self):
        self.public_key = "WOcgNWaMW6HoAB6jT+ny46ELXVOXW5uvaWrwwY5Nr3/zRndjo+SgxA=="
        self.private_key = "214963043d6f08ea51eb54774730c55d05ffb511"

    # "C:/programs/goodsdl2/goods/choose_goods/lishu_util/w.jpg"
    def download(self,ucloud_file_name,localfile_path_name):
        """
        文件下载
        ucloud_file_name: 在ucloud的名字
        localfile_path_name：在本地的路径和名字

        状态码描述：
            200：文件或者数据下载成功
            206：文件或者数据范围下载成功
            400：不存在的空间
            403：API公私钥错误
            401：下载签名错误
            404：下载文件或数据不存在
            416：文件范围请求不合法
        :return:
        改成数据流形式的下载（改源码）：
        httprequest.py文件的185行改成以下
            blocks = bytes()
            if response.status_code in [200, 206]:
                # with open(localfile, 'wb') as fd:
                    for block in response.iter_content(config.BLOCKSIZE):
                        # fd.write(block)
                        blocks += block
            else:
                return __return_wraper(response)
            return __return_wraper(response, True),BytesIO(blocks)  # 二进制数据流blocks
        改本方法的代码：
            (ret, resp),byte_stream = downloadufile_handler.download_file(public_bucket, put_key,localfile_path_name, isprivate=False)
            print(resp.status_code)
            roiImg = Image.open(byte_stream)
            # 图片保存
            roiImg.save(localfile_path_name)
            if resp.status_code == 200:
                return byte_stream
            else:
                return False
        """
        public_bucket = 'louxia'  # 公共空间名称
        public_savefile = ''  # 保存文件名
        range_savefile = ''  # 保存文件名
        put_key = '{}'.format(ucloud_file_name)  # 文件在空间中的名称
        stream_key = ''  # 文件在空间中的名称

        downloadufile_handler = filemanager.FileManager(self.public_key, self.private_key)

        # 从公共空间下载文件
        ret, resp = downloadufile_handler.download_file(public_bucket, put_key,localfile_path_name, isprivate=False)
        print(resp.status_code)
        if resp.status_code == 200:
            return True
        else:
            return False

    def upload(self,ucloud_file_name,localfile_path_name):
        """
        文件上传
        ucloud_file_name: 在ucloud的名字
        localfile_path_name：在本地的路径和名字
        状态码描述：
            200：文件或者数据上传成功
            400：上传到不存在的空间
            403：API公私钥错误
            401：上传凭证错误
        :return:
        """
        public_bucket = 'louxia'  # 公共空间名称
        # localfile = 'C:/Users/86130/Pictures/BlueDream_4k.jpg'  # 本地文件名
        put_key = '{}'.format(ucloud_file_name)  # 上传文件在空间中的名称


        putufile_handler = filemanager.FileManager(self.public_key, self.private_key)

        # 普通上传文件至公共空间
        ret, resp = putufile_handler.putfile(public_bucket, put_key, localfile_path_name, header=None)
        print(resp.status_code)
        # assert resp.status_code == 200
        if resp.status_code == 200:
            return True
        else:
            return False

    def stream_upload(self,ucloud_file_name,stream):
        """
        文件上传
        ucloud_file_name: 在ucloud的名字
        localfile_path_name：在本地的路径和名字
        状态码描述：
            200：文件或者数据上传成功
            400：上传到不存在的空间
            403：API公私钥错误
            401：上传凭证错误
        :return:
        """
        public_bucket = 'louxia'  # 公共空间名称
        # localfile = 'C:/Users/86130/Pictures/BlueDream_4k.jpg'  # 本地文件名

        putufile_handler = filemanager.FileManager(self.public_key, self.private_key)

        # 普通上传二进制数据流至公共空间
        # with open(localfile_path_name, 'rb') as f:
        #     a = f.read()
        byte_stream = BytesIO(stream)  # 二进制数据流
        stream_key = '{}'.format(ucloud_file_name)  # 上传数据流在空间中的名称
        ret, resp = putufile_handler.putstream(public_bucket, stream_key, byte_stream)
        print(resp.status_code)
        if resp.status_code == 200:
            return True
        else:
            return False

    def delete(self,ucloud_file_name):
        """
        删除文件
        状态码含义：
            204: 文件或者数据删除成功
            403: API公私钥错误
            401: 签名错误
        :return:
        """
        public_bucket = 'louxia'  # 公共空间名称
        delete_key = '{}'.format(ucloud_file_name)  # 文件在空间中的名称

        deleteufile_handler = filemanager.FileManager(self.public_key, self.private_key)

        # 删除公共空间的文件
        ret, resp = deleteufile_handler.deletefile(public_bucket, delete_key)
        # assert resp.status_code == 204
        print(resp.status_code)
        if resp.status_code == 204:
            return True
        else:
            return False


if __name__ == '__main__':
    m = FileManager()
    # m.upload('demo1.jpg','C:/programs/goodsdl2/goods/choose_goods/lishu_util/demo.jpg',True)
    m.download('demo1.jpg','C:/programs/goodsdl2/goods/choose_goods/lishu_util/q1.jpg')

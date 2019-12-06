import json
import requests
import main.import_django_settings
from django.conf import settings

def send_message(msg):
    is_test_server = settings.IS_TEST_SERVER
    if is_test_server:
        access_token = '5200bc97f99cf1b46fdefa32e5334e45dcc92080b9276a39c3a8832b0675a840'
    else:
        access_token = '6ebf5a764bd2e89c47e60a388208c67698bcb7f851aa4d7fd1745e8be427ec82'

    url = "https://oapi.dingtalk.com/robot/send?access_token={}".format(access_token)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    msg_json = {"msgtype": "text",
                "text": {
                    "content": "业务报警：{}".format(msg)
                }
                }
    json_info = json.dumps(msg_json)

    data = bytes(json_info, 'utf8')
    resp = requests.post(url=url, data=data, headers=headers)
    print('业务报警发送结果：{}'.format(resp))


if __name__ == "__main__":
    send_message('测试信息！')

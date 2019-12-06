import json
import requests
import main.import_django_settings
from django.conf import settings

def send_message(msg):
    is_test_server = settings.IS_TEST_SERVER
    if is_test_server:
        type = '(测试)'
    else:
        type = ''

    url = "https://oapi.dingtalk.com/robot/send?access_token=6ebf5a764bd2e89c47e60a388208c67698bcb7f851aa4d7fd1745e8be427ec82"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    msg_json = {"msgtype": "text",
                "text": {
                    "content": "业务报警{}：{}".format(type, msg)
                }
                }
    json_info = json.dumps(msg_json)

    data = bytes(json_info, 'utf8')
    resp = requests.post(url=url, data=data, headers=headers)
    print('业务报警发送结果：{}'.format(resp))


if __name__ == "__main__":
    send_message('测试信息！')

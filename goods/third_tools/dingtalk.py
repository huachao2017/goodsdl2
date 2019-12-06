import json
import requests
import main.import_django_settings
from django.conf import settings

def send_message(msg, type = 0):
    """

    :param msg:
    :param type: 0其他业务报警，1是选品，2是陈列，3是订货
    :return:
    """
    is_test_server = settings.IS_TEST_SERVER
    if is_test_server:
        access_token = '5200bc97f99cf1b46fdefa32e5334e45dcc92080b9276a39c3a8832b0675a840'
    else:
        access_token = '6ebf5a764bd2e89c47e60a388208c67698bcb7f851aa4d7fd1745e8be427ec82'

    if type == 1:
        alert_name = '选品报警'
    elif type == 2:
        alert_name = '陈列报警'
    elif type == 3:
        alert_name = '订货报警'
    else:
        alert_name = '业务报警'

    url = "https://oapi.dingtalk.com/robot/send?access_token={}".format(access_token)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    msg_json = {"msgtype": "text",
                "text": {
                    "content": "{}：{}".format(alert_name, msg)
                }
                }
    json_info = json.dumps(msg_json)

    data = bytes(json_info, 'utf8')
    resp = requests.post(url=url, data=data, headers=headers)
    print('业务报警发送结果：{}'.format(resp))


if __name__ == "__main__":
    send_message('测试信息！')

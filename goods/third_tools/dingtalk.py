import json
import requests

def send_message(msg):
    url = "https://oapi.dingtalk.com/robot/send?access_token=6ebf5a764bd2e89c47e60a388208c67698bcb7f851aa4d7fd1745e8be427ec82"
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

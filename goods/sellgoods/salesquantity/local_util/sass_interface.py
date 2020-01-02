import urllib.request
import time
from set_config import config
import traceback
def order_commit(batch_id,msg=''):
    try:

        url =  config.shellgoods_params["sass_order_url"]
        print("notify sass , batch_id={},msg={}".format(str(batch_id),str(msg)))
        index = 0
        while True:
            try:
                request = urllib.request.Request(url=url.format(str(batch_id),str(msg)))
                response = urllib.request.urlopen(request)
                print(response.read().decode())
                break
            except Exception as e:
                index += 1
                if index > 5:
                    # raise e
                    break
                print('notify sass error:{}'.format(e))
                traceback.print_exc()
                time.sleep(1)
                continue
    except Exception as e:
        print('notify sass error:{}'.format(e))
        traceback.print_exc()

if __name__ == "__main__":
    order_commit(1284,0)
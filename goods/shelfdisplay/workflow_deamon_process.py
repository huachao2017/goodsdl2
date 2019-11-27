import time
import os
import sys
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()

from goods.shelfdisplay.generate_shelf_display import generate_workflow_displays
from goods.models import AllWorkFlowBatch


class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

if __name__ == "__main__":
    path = os.path.abspath(os.path.dirname(__file__))
    type = sys.getfilesystemencoding()
    sys.stdout = Logger('/home/src/goodsdl2/goods/shelfdisplay/log')
    while True:
        time.sleep(60)
        print('workflow deamon is alive')

        try:
            workflows = AllWorkFlowBatch.objects.filter(auto_display_status=1).all()
            for workflow in workflows:
                generate_workflow_displays(workflow.uc_shopid, workflow.batch_id)
        except Exception as e:
            print('守护进程出现错误：{}'.format(e))

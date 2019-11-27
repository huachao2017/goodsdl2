import time
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()

from goods.shelfdisplay.generate_shelf_display import generate_workflow_displays
from goods.models import AllWorkFlowBatch


if __name__ == "__main__":

    while True:
        time.sleep(60)

        try:
            workflows = AllWorkFlowBatch.objects.filter(auto_display_status=1).all()
            for workflow in workflows:
                generate_workflow_displays(workflow.uc_shopid, workflow.batch_id)
        except Exception as e:
            print('守护进程出现错误：{}'.format(e))

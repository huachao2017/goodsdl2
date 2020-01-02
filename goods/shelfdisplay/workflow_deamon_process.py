import time
import traceback
import main.import_django_settings

from django.db import close_old_connections

from goods.models import AllWorkFlowBatch
from goods.shelfdisplay.generate_shelf_display import generate_workflow_displays

# class Logger(object):
#     def __init__(self, filename="Default.log"):
#         self.terminal = sys.stdout
#         self.log = open(filename, "a")
#
#     def write(self, message):
#         self.terminal.write(message)
#         self.log.write(message)
#
#     def flush(self):
#         pass

if __name__ == "__main__":
    # sys.stdout = Logger('/home/src/goodsdl2/logs/display.log')
    while True:
        print('workflow deamon is alive')
        close_old_connections()

        try:
            workflows = AllWorkFlowBatch.objects.filter(auto_display_status=1).all()
            for workflow in workflows:
                try:
                    begin_time = time.time()
                    generate_workflow_displays(workflow.uc_shopid, workflow.batch_id)
                    end_time = time.time()
                    auto_display_calculate_time = int(end_time - begin_time)
                    # 更新workflow
                    workflow.auto_display_status = 3
                    workflow.auto_display_calculate_time = auto_display_calculate_time
                    workflow.save()
                except Exception as e:
                    traceback.print_exc()
                    print('陈列出现错误：{}'.format(e))
                    # 更新workflow
                    workflow.auto_display_status = 4
                    workflow.auto_display_calculate_time = 0
                    workflow.save()

        except Exception as e:
            print('守护进程出现错误：{}'.format(e))

        time.sleep(10)

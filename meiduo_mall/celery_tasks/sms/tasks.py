# 生产者----任务，函数
# 1.这个函数必须让celery的实例的task装饰器装饰
# 2.需要celery自动检测指定包的任务
from libs.yuntongxun.sms import CCP
from celery_tasks.main import app

@app.task
def celery_send_sms_code(mobile,sms_code):
    ccp = CCP()
    ccp.send_template_sms(mobile,[sms_code,5],1)

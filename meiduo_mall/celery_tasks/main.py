import os
from celery import Celery

# 1.为celery的运行，配置django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings')
# 2.创建celery实例
# 参数1：main设置脚本路径就可以，脚本路径是唯一的
app = Celery('celery_tasks')

# 3.设置broker
# 我们通过加载配置文件来设置broker
app.config_from_object('celery_tasks.config')

# 4.需要celery自动检测指定的包的任务
# autodiscover_tasks参数是列表
# 列表中的元素是tasks的路径
app.autodiscover_tasks(['celery_tasks.sms'])

# 启动消费者worker终端指令
# windows系统必须用如下指令运行，否则worker不工作
# celery -A celery_tasks.main worker -l info -P eventlet  -c 10
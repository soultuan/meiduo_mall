from django.core.files.storage import Storage

class MyStorage(Storage):
    def _open(self, name, mode="rb"):
        pass

    def _save(self, name, content, max_length=None):
        pass
    # 重写url方法，把路径改为访问minio图片的路径
    def url(self,name):
        return "127.0.0.1:9005/" + name

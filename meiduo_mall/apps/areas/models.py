from django.db import models

# Create your models here.
class Area(models.Model):
    """省市县"""
    name = models.CharField(max_length=20,verbose_name='名称')
    parent = models.ForeignKey('self',on_delete=models.SET_NULL,related_name='subs',null=True,blank=True,verbose_name='上级行政区划')

    # related_name是关联模型的名字
    # 默认是 关联模型类名小写_set area_set
    # 可以通过related_name修改默认名字,现在改成subs

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '省市区'
        verbose_name_plural = '省市区'

    def __str__(self):
        return self.name
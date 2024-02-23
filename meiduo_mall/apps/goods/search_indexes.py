from apps.goods.models import SKU
from haystack import indexes

"""
0.在模型对应的子应用中创建search——indexes.py文件，以方便haystack检索数据
1.索引类必须继承indexes.SearchIndex,indexes.Indexable
2.必须定义一个字段document=true
    字段名是什么都可以，text是惯例
    所有的索引的这个字段都一致就行
3.use_template=True
    允许单独设置一个文件，来指定哪些字段进行检索
    这个单独的文件在模板文件下/search/indexes/子应用目录/模型类名小写_text.txt
    
运作：让haystack将数据获取给es来生成索引
在虚拟环境下运行 python manage.py rebuild_index
"""
class SKUIndex(indexes.SearchIndex,indexes.Indexable):
    text = indexes.CharField(document=True,use_template=True)

    def get_model(self):
        return SKU

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_launched=True)

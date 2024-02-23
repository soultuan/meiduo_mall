#!/usr/bin/env python
# ../当前目录的上一级目录,也就是base_dir
import sys
sys.path.insert(0,'../')
# 我们的django的配置文件位置
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','meiduo_mall.settings')
# django setup
import django
django.setup()

from utils.goods import get_categories,get_breadcrumb,get_goods_specs
from meiduo_mall import settings
from apps.goods.models import SKU
from django.template import loader

def generic_meiduo_detail(sku):
    # try:
    #     sku = SKU.objects.get(id=sku_id)
    # except SKU.DoesNotExist:
    #     pass
    # 1.分类数据
    categories = get_categories()
    # 2.面包屑
    breadcrumb = get_breadcrumb(sku.category)
    # 3.SKU信息
    # 4.规格信息
    goods_specs = get_goods_specs(sku)
    context = {
        'categories': categories,
        'breadcrumb': breadcrumb,
        'sku': sku,
        'specs': goods_specs,
    }
    # 1.加载渲染时的模板
    detail_template = loader.get_template('templates/detail.html')
    # 2.把数据给模板
    detail_html_data = detail_template.render(context)
    # base_dir的上一级
    file_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'front_end_pc/goods/%s.html' % sku.id)
    with open(file_path, 'w', encoding='utf8') as f:
        f.write(detail_html_data)
    print(sku.id)

skus = SKU.objects.all()
for sku in skus:
    generic_meiduo_detail(sku)
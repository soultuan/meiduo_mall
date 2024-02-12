from django.shortcuts import render
from django.views import View
from apps.areas.models import Area
from django.http import JsonResponse
from django.core.cache import cache
# Create your views here.
class AreaView(View):
    def get(self,request):
        # 先查询缓存数据
        province_list = cache.get('province_list')
        if province_list is None:
            # 1.查询省份信息
            # 返回的province是查询结果集->queryset格式
            provinces = Area.objects.filter(parent=None)
            # 2.将对象转换成字段数据
            province_list = []
            for province in provinces:
                province_list.append({
                    'id':province.id,
                    'name':province.name
                })
                # 保存缓存数据
            cache.set('province_list',province_list,24*3600)
        # 3.返回响应
        return JsonResponse({'code':0,'errmsg':'ok','province_list':province_list})

class SubAreaView(View):
    def get(self,request,id):
        subs = cache.get(f'subs_{id}')
        if subs is None:
            # 1.获取省份id，市id，查询信息
            up_level = Area.objects.get(id=id)
            down_level = up_level.subs.all()
            # 2.将对象转换成字典数据
            subs = []
            for item in down_level:
                subs.append({
                    'id':item.id,
                    'name':item.name
                })
            cache.set(f'subs_{id}',subs,24*3600)
        # 3.返回响应
        return JsonResponse({'code':0,'errmsg':'ok','sub_data':{'subs':subs}})
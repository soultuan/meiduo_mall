from django.shortcuts import render
from django.views import View
from apps.areas.models import Area
from django.http import JsonResponse
# Create your views here.
class AreaView(View):
    def get(self,request):
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
        # 3.返回响应
        return JsonResponse({'code':0,'errmsg':'ok','province_list':province_list})
from django.shortcuts import render
from minio import Minio
from minio.error import S3Error
from django.views import View
from utils.goods import get_categories,get_breadcrumb
from apps.contents.models import ContentCategory
from apps.goods.models import GoodsCategory,SKU
from django.http import JsonResponse
from django.core.paginator import Paginator
from haystack.views import SearchView
#
# # MinIO 服务的基本连接信息
# minio_client = Minio(
#     '127.0.0.1:9005',
#     access_key='minioadmin',
#     secret_key='minioadmin',
#     secure=False
# )
#
# # 要上传的本地文件路径和 MinIO 上的桶名称和文件对象名称
# local_file_path = "C:/Users/76330/Pictures/Saved Pictures/my.jpg"
# bucket_name = 'my-bucket'
# object_name = 'my-object'
#
# # 检查桶是否存在，如果不存在则创建
# if not minio_client.bucket_exists(bucket_name):
#     minio_client.make_bucket(bucket_name)
#
# # 上传文件
# try:
#     minio_client.fput_object(bucket_name, object_name, local_file_path)
#     print("文件上传成功")
# except S3Error as e:
#     print("文件上传失败", e)

class IndexView(View):
    def get(self,request):
        # 1.商品分类数据
        categories = get_categories()
        # 2.广告数据
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        context = {
            'categories':categories,
            'contents':contents,
        }
        return render(request,'index.html',context)

class ListView(View):
    def get(self,request,category_id):
        # 1.接收字段
        # 第几页数据字段
        page = request.GET.get('page')
        # 每页多少条数据
        page_size = request.GET.get('page_size')
        # 排序字段
        ordering = request.GET.get('ordering')
        # 2.获取分类id
        # 3.根据分类id进行分类数据的查询验证
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'参数缺失'})
        # 4.获得面包屑数据
        breadcrumb = get_breadcrumb(category)
        # 分页
        skus = SKU.objects.filter(category=category,is_launched=True).order_by(ordering)
        paginator = Paginator(skus,per_page=page_size)
        page_skus = paginator.page(page)
        skus_list = []
        for sku in page_skus.object_list:
            skus_list.append({
                'id':sku.id,
                'name':sku.name,
                'price':sku.price,
                'default_image_url':sku.default_image.url
            })
        # 获得总页数
        count = paginator.num_pages
        # 6.返回响应
        return JsonResponse({'code':0,'errmsg':'ok','list':skus_list,'count':count,'breadcrumb':breadcrumb})

class ListHotView(View):
    def get(self,request,cat_id):
        try:
            category = GoodsCategory.objects.get(id=cat_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'参数缺失'})
        # 分页
        skus = SKU.objects.filter(category=category,is_launched=True)
        skus_list = []

        count = 0
        for sku in skus:
            if count == 4:
                break
            skus_list.append({
                'id':sku.id,
                'name':sku.name,
                'price':sku.price,
                'default_image_url':sku.default_image.url
            })
            count += 1

        return JsonResponse({'code':0,'errmsg':'ok','hot_skus':skus_list})


# 我们借助haystack来对接es，所以haystack可以帮助查询数据
# haystack.views的searchView中的create_response能返回响应，但是返回的不是json数据，所以需要重写这个方法
class SKUSearchView(SearchView):
    def create_response(self):
        # 获取搜索结果
        context = self.get_context()
        # 通过添加端点来分析context中的数据格式
        sku_list = []
        for sku in context['page'].object_list:
            sku_list.append({
                'id':sku.object.id,
                'name':sku.object.name,
                'price':sku.object.price,
                'default_image_url':sku.object.default_image.url,
                'searchkey':context.get('query'),
                'page_size':context['page'].paginator.num_pages,
                'count':context['page'].paginator.count
            })
        return JsonResponse(sku_list,safe=False)
# http://172.16.34.33:8001/admin/scanUpdate 链接下展示资源扫描各项目详细信息页面的服务器端代码
# 记得在views/admin/__init__.py也加上新增的路由
from pyexpat.errors import messages
from rest_framework.decorators import api_view, authentication_classes

from myapp import utils
from myapp.auth.authentication import AdminTokenAuthtication
from myapp.handler import APIResponse
from myapp.models import ScanUpdate
from myapp.permission.permission import isDemoAdminUser
from myapp.serializers import ScanUpdateSerializer, UpdateScanUpdateSerializer


@api_view(['GET'])
def list_api(request):
    if request.method == 'GET':
        # keyword是当有搜索栏对应搜索内容时使用，没有搜索内容则为空
        keyword = request.GET.get("keyword", None)
        if keyword:
            scanUpdates = ScanUpdate.objects.filter(name__contains=keyword).order_by('id')
        else:
            scanUpdates = ScanUpdate.objects.all().order_by('id')
        # serializer: 将服务端的数据结构（如模型类对象）转换为客户端可接受的格式（如字典、JSON），
        # 同时也能将客户端的数据（如JSON）转换为服务端的数据结构。这种转换过程包括序列化（将数据转换为可传输的格式）和反序列化（将传输格式的数据还原为Python数据类型）
        serializer = ScanUpdateSerializer(scanUpdates, many=True)
        return APIResponse(code=0, msg='查询成功', data=serializer.data)


@api_view(['GET'])
def detail(request):

    try:
        pk = request.GET.get('id', -1)
        scanUpdates = ScanUpdate.objects.get(pk=pk)
    except ScanUpdate.DoesNotExist:
        utils.log_error(request, '对象不存在')
        return APIResponse(code=1, msg='对象不存在')

    if request.method == 'GET':
        serializer = ScanUpdateSerializer(scanUpdates)
        return APIResponse(code=0, msg='查询成功', data=serializer.data)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def create(request):

    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')

    serializer = ScanUpdateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return APIResponse(code=0, msg='创建成功', data=serializer.data)
    else:
        print(serializer.errors)
        utils.log_error(request, '参数错误')

    return APIResponse(code=1, msg='创建失败')


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def update(request):

    # 判断是否是演示账号，用于账号隔离
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')

    try:
        # 在数据库中能否搜索到对应id，没有的话则为-1
        # pk‌：代表主键（Primary Key），是每个模型的主键字段。在大多数情况下，主键字段名为id
        pk = request.GET.get('id', -1)
        scanUpdates = ScanUpdate.objects.get(pk=pk)

    except ScanUpdate.DoesNotExist:
        return APIResponse(code=1, msg='对象不存在')

    serializer = UpdateScanUpdateSerializer(scanUpdates, data=request.data)
    print(serializer)
    if serializer.is_valid():
        serializer.save()
        return APIResponse(code=0, msg='项目信息更新成功', data=serializer.data)
    else:
        print(serializer.errors)
        utils.log_error(request, '参数错误')

    return APIResponse(code=1, msg='项目信息更新失败')


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def delete(request):

    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')

    try:
        ids = request.GET.get('ids')
        ids_arr = ids.split(',')
        ScanUpdate.objects.filter(id__in=ids_arr).delete()
    except ScanUpdate.DoesNotExist:
        return APIResponse(code=1, msg='对象不存在')
    return APIResponse(code=0, msg='删除成功')

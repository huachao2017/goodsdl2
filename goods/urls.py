"""dlserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from goods import views,views_shelf,views_shelf2, views_display, views_arm

router = DefaultRouter()

router.register(r'shelfimage', views_shelf.ShelfImageViewSet)
router.register(r'shelfgoods', views_shelf.ShelfGoodsViewSet)
router.register(r'shelfimage2', views_shelf2.ShelfImageViewSet)
router.register(r'shelfgoods2', views_shelf2.ShelfGoodsViewSet)
router.register(r'freezerimage', views.FreezerImageViewSet)
router.register(r'mengniufreezerimage', views.MengniuFreezerImageViewSet)
router.register(r'goodswh', views.GoodsImageViewSet)
router.register(r'workflowbatch', views.AllWorkFlowBatchViewSet)
router.register(r'shelfdisplay', views_display.ShelfDisplayDebugViewSet)

arm_router = DefaultRouter()
arm_router.register(r'detect', views_arm.ArmImageViewSet)
urlpatterns = [
    url(r'^test', views.Test.as_view()),
    url(r'^api/shelf_score', views_shelf.ShelfScore.as_view()),
    url(r'^api/rectify_detect', views_shelf.RectifyAndDetect.as_view()),
    url(r'^api/get_shelfimage', views_shelf.GetShelfImage.as_view()),
    url(r'^api/shelfimage_detail', views_shelf.GetShelfImageDetail.as_view()),
    url(r'^api/detect_shelfimage', views_shelf.DetectShelfImage.as_view()),
    url(r'^api/createshelfimage2', views_shelf2.CreateShelfImage.as_view()),
    url(r'^api/rectifyshelfimage2', views_shelf2.RectifyShelfImage.as_view()),
    # url(r'^api/notify_generate_shop_add', views_sellgoods.SellGoodsViewSet.as_view()),
    url(r'^api/beginselectgoods', views.BeginSelectGoods.as_view()),
    url(r'^api/beginautodisplay', views.BeginAutoDisplay.as_view()),
    url(r'^api/beginordergoods', views.BeginOrderGoods.as_view()),
    url(r'^api/orderconfirm', views.OrderConfirm.as_view()),
    url(r'^api/', include(router.urls)),
    url(r'^arm/', include(arm_router.urls))
]

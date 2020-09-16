"""sampleapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token  
from django.conf.urls.i18n import i18n_patterns 
from django.conf.urls import include
from .views import *
from rest_framework import routers
from django.contrib.auth import views as auth_views

router = routers.DefaultRouter()
router.register('workorder', WorkOrderViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    
    path('api/work_order_list', WorkOrderListView.as_view(), name="work_order_list"),
    path('api/work_order/create', create_work_order, name="create_work_order"),
    path('api/work_order/<int:pk>', detail_work_order, name="detail_work_order"),
    path('api/work_order/update/<int:pk>', update_work_order, name="update_work_order"),
    path('api/work_order/delete/<int:pk>', delete_work_order, name="delete_work_order"),
    path('api/is_creator_of_work_order/<int:pk>', is_creator_of_work_order, name="is_creator_of_work_order"),

    path('api/check_if_account_exists/', does_account_exist_view, name="check_if_account_exists"),
	path('api/change_password/', ChangePasswordView.as_view(), name="change_password"),
	path('api/properties', account_properties_view, name="properties"),
	path('api/properties/update', update_account_view, name="update"),
 	path('api/login', ObtainAuthTokenView.as_view(), name="login"), 
	path('api/register', registration_view, name="register"),
  	path('api/password_reset_request', password_reset_request, name="password_reset_request"),
    path('reset/<str:uidb64>/<str:token>/', auth_views.PasswordResetConfirmView.as_view(template_name="sampleapp/registration/password_reset_confirm.html"),  name='password_reset_confirm'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="sampleapp/registration/password_reset_done.html"),  name='password_reset_done'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='sampleapp/registration/password_reset_complete.html'), name='password_reset_complete'),      
    path('', index, name="index"),

]

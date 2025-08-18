"""
URL configuration for sent_main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from . import views
from overall_file_sent import views as file_sent_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name='home'),
    path('file_overall',file_sent_views.file_overall,name='file_overall'),
    path('login-createacc',views.login_create_acc,name='login_create_acc'),
    path('logout',views.logout,name='logout'),
    path('analysis_search',file_sent_views.analysis_search,name='analysis_search'),
    path('analysis_viwer/<int:pk>',file_sent_views.analysis_viwer,name='analysis_viwer'),
    path('analysis_viwer/<int:pk>/delete_analysis',file_sent_views.delete_analysis,name='delete_analysis'),
    path('analysis_viwer/<int:pk>/update',file_sent_views.update_analysis,name='update')

]

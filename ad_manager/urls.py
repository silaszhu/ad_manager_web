# -*- coding: utf-8 -*-
"""testapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from ad_manager import views

urlpatterns = (
    # url(r'^$', views.home),
    url(r'^$', views.index),
    url(r'^contact/$', views.contact),
    # url(r'^main_page', views.main_page),
    url(r'^search_statistic_data$', views.search_statistic_data),
    url(r'^search_statistic_data2$', views.search_statistic_data2),
    url(r'^search_reports_dataset$', views.search_reports_dataset),
    url(r'^search_fields$', views.search_fields),
    url(r'^download_excel$', views.download_excel)
)

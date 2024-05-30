from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload_file'),
    path('download_buy_pdf/', views.download_buy_pdf, name='download_buy_pdf'),
    path('download_buy_excel/', views.download_buy_excel, name='download_buy_excel'),
    path('download_sell_pdf/', views.download_sell_pdf, name='download_sell_pdf'),
    path('download_sell_excel/', views.download_sell_excel, name='download_sell_excel'),
]

from django.contrib import admin
from django.urls import path
from stock_chart.views import stock_chart

urlpatterns = [
    path('', stock_chart, name='home'),  # Đây là URL cho trang chính
    path('admin/', admin.site.urls),
    path('stock_chart/', stock_chart, name='stock_chart'),
]

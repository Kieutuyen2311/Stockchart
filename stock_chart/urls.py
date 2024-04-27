from django.urls import path
from . import views

urlpatterns = [
    path('stock_chart/', views.stock_chart, name='stock_chart'),
]

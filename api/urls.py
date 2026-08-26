from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.ProductList.as_view(), name='product_list'),
    path('create/', views.CreateProductList.as_view(), name='create_product'),
    path('edit/<int:pk>/', views.EditProductList.as_view(), name='edit_product'),
    path('test/', views.test.as_view(), name='test'),
]
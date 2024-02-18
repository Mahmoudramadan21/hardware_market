from django.urls import path
from api.views import product_views as views

urlpatterns = [

    path('', views.getProducts, name="products"),
    path('top/', views.getTopProducts, name='top-products'),

    path('category/<str:name>/', views.getCategoryOfProducts, name="product-category"),
    path('<int:pk>/', views.getProduct, name="product"),

    path('create/', views.createProduct, name="product-create"),
    path('update/<int:pk>/', views.updateProduct, name="product-update"),
    path('delete/<int:pk>/', views.deleteProduct, name="product-delete"),

    path('<int:pk>/reviews/', views.createProductReview, name="create-review"),
]
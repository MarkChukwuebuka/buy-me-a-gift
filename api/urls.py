from .views import *
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

app_name = 'api'

urlpatterns = [
    # auth
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name="login"),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("password-reset/", PasswordResetView.as_view(), name="password-reset"),
    path("password-reset-confirm/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    

    # product
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('product/detail/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('product/delete/<int:pk>/', ProductDeleteAPIView.as_view(), name='product-delete'),
    path('product/update/<int:pk>/', ProductUpdateAPIView.as_view(), name='product-update'),
    path('product/create/', ProductCreateAPIView.as_view(), name='product-create'),

    # category
    path('category/create/', CategoryCreateAPIView.as_view(), name='category-create'),
    path('category/list/', CategoryListAPIView.as_view(), name='category-list'),
    path('category/delete/<int:pk>/', CategoryDeleteAPIView.as_view(), name='category-delete'),

    # wishlist
    # path('wishlist/', WishListView.as_view(), name='wishlist-create'),
    # path('wishlist/view/', WishListProductListView.as_view(), name='wishlist-view'),
    # path('wishlist/<str:pk>/view/', WishListProductListViewByIdentifier.as_view(), name='wishlist-view'),



    
]
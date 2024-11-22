from django.urls import path
from .views import (
    ProductView,
    DiscountView,
    ProductIndexView,
    CategoryView,
    ProductAggregationView,
    ProductTemporalView,
)

urlpatterns = [
    path('products/', ProductView.as_view()),
    path('products/discount/', DiscountView.as_view()),
    path('products/index/', ProductIndexView.as_view()),
    path('products/temporal/', ProductTemporalView.as_view()),
    path('products/statistics/<str:func>', ProductAggregationView.as_view()),
    path('products/<str:pk>/category/', CategoryView.as_view()),
    path('products/<str:pk>/', ProductView.as_view()),
]
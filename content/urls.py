from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'admin/sections', views.AdminSectionViewSet, basename='admin-sections')
router.register(r'admin/items', views.AdminItemViewSet, basename='admin-items')
router.register(r'admin/users', views.UserViewSet, basename='admin-users')

urlpatterns = [
    path('auth/login/', views.login_view),
    path('auth/me/', views.me_view),

    path('pages/', views.PageListView.as_view()),
    path('pages/<slug:slug>/', views.PageDetailView.as_view()),
    path('site-settings/', views.site_settings_view),

    path('admin/site-settings/', views.admin_site_settings),
    path('admin/upload/', views.upload_image),

    path('', include(router.urls)),
]

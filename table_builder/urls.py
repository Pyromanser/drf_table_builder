from django.urls import include, path

from rest_framework import routers

from table_builder import views

router = routers.DefaultRouter()
router.register(r'table', views.DynamicTableViewSet, basename='table')

app_name = 'table_builder'
urlpatterns = [
    path('', include(router.urls)),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('predict/', views.predict, name='predict'),
    path('test-sentry/', views.trigger_sentry_error, name='test_sentry'),
    path('sentry-tunnel/', views.sentry_tunnel, name='sentry_tunnel'),
]

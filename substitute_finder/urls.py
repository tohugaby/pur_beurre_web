from django.urls import path

from .views import index


app_name = 'substitute_finder'


urlpatterns = [
    path('', index, name='index')
]

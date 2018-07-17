from django.urls import path, include

from .views import index, login_view, logout_view


app_name = 'substitute_finder'


urlpatterns = [
    path('', index, name='index'),
    #path('accounts/', include('django.contrib.auth.urls')),
    path('login', login_view, name='login'),
    path('logout', logout_view, name='logout')
]

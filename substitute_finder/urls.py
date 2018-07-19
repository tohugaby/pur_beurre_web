from django.urls import path, include

from .views import index, account, create_account,login_view, logout_view


app_name = 'substitute_finder'


urlpatterns = [
    path('', index, name='index'),
    path('account/', account, name='account'),
    path('create-account/', create_account, name='create_account'),
    path('login', login_view, name='login'),
    path('logout', logout_view, name='logout')
]

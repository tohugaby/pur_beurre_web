"""
substitute_finder app urls
"""
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import path, include
from rest_framework import routers

from substitute_finder.views import comment_list_view
from substitute_finder.viewsets import CommentApiViewSet, CategoryApiViewSet, ProductApiViewSet, CustomUserApiViewSet
from substitute_finder.viewsets import CommentsByProductApiView
from .views import account_view, search_view, product_view, create_account_view, index_view, login_view, \
    logout_view, add_favorite_view, favorites_view, legal_view

app_name = 'substitute_finder'

router = routers.DefaultRouter()
router.register('users', CustomUserApiViewSet)
router.register('categories', CategoryApiViewSet)
router.register('products', ProductApiViewSet)
router.register('comments', CommentApiViewSet)

urlpatterns = [
    path('', index_view, name='index'),
    path('search', search_view, name='search'),
    path('product/<pk>', product_view, name='product'),
    path('product/<pk>/comments', comment_list_view, name='comments'),
    url(r'^api/', include(router.urls)),
    url('products/(?P<pk>\d+)/comments-list/$', CommentsByProductApiView.as_view(), name='comments_list'),

    path('add-favorite/<pk>', add_favorite_view, name='add_favorite'),
    path('favorites', favorites_view, name='favorites'),
    path('legal', legal_view, name='legal'),

    path('account/', account_view, name='account'),
    path('create-account/', create_account_view, name='create_account'),
    path('login', login_view, name='login'),
    path('logout', logout_view, name='logout'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/custom_password_reset_form.html',
        success_url='/accounts/password_reset/done/',
        email_template_name='registration/custom_password_reset_email.html'
    ),
         name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/custom_password_reset_done.html',
    ),
         name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        success_url='/accounts/reset/done/',
        template_name='registration/custom_password_reset_confirm.html'
    ),
         name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/custom_password_reset_complete.html'
    ),
         name='password_reset_complete'),
]

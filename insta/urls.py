from django.contrib import admin
from django.urls import path, include

from . import views


urlpatterns = [
    path('add-pk/', views.add_pk_view, name='add_pk_url'),
    path('posting/<str:user_key>', views.posting_view, name='posting_url'),
    path('random-comment/', views.random_comment_view, name='random_comment_url'),
    path('login/<str:target_user_key>', views.login_page_view, name='login_page_url'),
]

from django.urls import path
from django.contrib.auth import views as auth_views

from .views import bookmark_create_view, bookmark_list_view, user_follow_view, register_view, my_bookmarks_view, \
    search_bookmarks_view, import_bookmarks

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='bookmark/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('bookmark/create/', bookmark_create_view, name='bookmark_create'),
    path('my-bookmarks/', my_bookmarks_view, name='my_bookmarks'),
    path('search/', search_bookmarks_view, name='search_bookmarks'),
    path('', bookmark_list_view, name='bookmark_list'),
    path('follow/<int:user_id>/', user_follow_view, name='user_follow'),
    path('import_bookmarks/',import_bookmarks, name='import_bookmarks'),
]
from django.urls import path
from task_manager.users.views import (
    UsersCreateView,
    UserLoginView,
    UserLogoutView,
    UserListView,
    UserUpdateView,
    UserDeleteView
)


app_name = 'users'


urlpatterns = [
    path('', UserListView.as_view(), name='index'),
    path('create/', UsersCreateView.as_view(), name='create'),
    path('<int:pk>/update/', UserUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', UserDeleteView.as_view(), name='delete'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
]

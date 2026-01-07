from django.urls import path

from task_manager.tasks.views import (
    TasksCreateView,
    TasksDeleteView,
    TasksDetailView,
    TasksListView,
    TasksUpdateView,
)

app_name = 'tasks'

urlpatterns = [
    path('', TasksListView.as_view(), name='index'),
    path('create/', TasksCreateView.as_view(), name='create'),
    path('<int:pk>/update/', TasksUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', TasksDeleteView.as_view(), name='delete'),
    path('<int:pk>/show/', TasksDetailView.as_view(), name='show'),
]

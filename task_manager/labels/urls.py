from django.urls import path
from task_manager.labels.views import (
    LabelsListView,
    LabelsCreateView,
    LabelsUpdateView,
    LabelsDeleteView,
)

app_name = 'labels'

urlpatterns = [
    path('', LabelsListView.as_view(), name='index'),
    path('create/', LabelsCreateView.as_view(), name='create'),
    path('<int:pk>/update/', LabelsUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', LabelsDeleteView.as_view(), name='delete'),
]

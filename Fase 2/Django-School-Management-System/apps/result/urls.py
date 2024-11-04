from django.urls import path

from .views import ResultListView, create_result, edit_results, subject_detail,subject_list

urlpatterns = [
    #path("create/", create_result, name="create-result"),
    path("edit-results/", edit_results, name="edit-results"),
    path("view/all", ResultListView.as_view(), name="view-results"),
    path('create/<int:subject_id>/', subject_detail, name='subject_detail'),
    path('subject/<int:subject_id>/add_results/', create_result, name='create_result'),
    path('subject_list/', subject_list, name='subject_list'),
]

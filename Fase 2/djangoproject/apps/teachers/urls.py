from django.urls import path

from .views import (
    TeacherCreateView,
    TeacherDeleteView,
    TeacherDetailView,
    TeacherListView,
    TeacherUpdateView,
    TeacherSubjectsListView,
    SubjectDetailView,
    AnnotationListView,
    AnnotationCreateView,
    TeacherAnnotationCreateView
)

urlpatterns = [
    path("list/", TeacherListView.as_view(), name="teacher-list"),
    path("<int:pk>/", TeacherDetailView.as_view(), name="teacher-detail"),
    path("create/", TeacherCreateView.as_view(), name="teacher-create"),
    path("<int:pk>/update/", TeacherUpdateView.as_view(), name="teacher-update"),
    path("<int:pk>/delete/", TeacherDeleteView.as_view(), name="teacher-delete"),
    path("<int:pk>/subjects/", TeacherSubjectsListView.as_view(), name='teacher-subjects-list'),
    path("subject/<int:pk>/", SubjectDetailView.as_view(), name='subject-detail'),
    path('annotations/', AnnotationListView.as_view(), name='annotation-list'),
    path('annotations/create/', AnnotationCreateView.as_view(), name='annotation-create'),
    path('annotations/<int:pk>/create/', TeacherAnnotationCreateView.as_view(), name='teacher-annotation-create'),

]

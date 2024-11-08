from django.urls import path
from . import views

from .views import (
    DownloadCSVViewdownloadcsv,
    StudentBulkUploadView,
    StudentCreateView,
    StudentDeleteView,
    StudentDetailView,
    StudentListView,
    StudentUpdateView,
    AttendanceListView
)

urlpatterns = [
    path("list", StudentListView.as_view(), name="student-list"),
    path("<int:pk>/", StudentDetailView.as_view(), name="student-detail"),
    path("create/", StudentCreateView.as_view(), name="student-create"),
    path("<int:pk>/update/", StudentUpdateView.as_view(), name="student-update"),
    path("delete/<int:pk>/", StudentDeleteView.as_view(), name="student-delete"),
    #path("upload/", StudentBulkUploadView.as_view(), name="student-upload"),
    #path("download-csv/", DownloadCSVViewdownloadcsv.as_view(), name="download-csv"),
    path('attendance/', AttendanceListView.as_view(), name='attendance-list'),
    path("download-csv/", views.generate_student_excel_template, name="download-student-template"),
    path("upload/", views.upload_student_excel, name="upload-student-excel"),

]

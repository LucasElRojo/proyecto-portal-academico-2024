from django.urls import path
from . import views

from .views import (
    ClassCreateView,
    ClassDeleteView,
    ClassListView,
    ClassUpdateView,
    CurrentSessionAndTermView,
    IndexView,
    SessionCreateView,
    SessionDeleteView,
    SessionListView,
    SessionUpdateView,
    SiteConfigView,
    SubjectCreateView,
    SubjectDeleteView,
    SubjectListView,
    SubjectUpdateView,
    TermCreateView,
    TermDeleteView,
    TermListView,
    TermUpdateView,
    attendance_register,
    get_estado_data,
    get_payment_distribution,
    get_kpi_data
)

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("site-config", SiteConfigView.as_view(), name="configs"),
    path(
        "current-session/", CurrentSessionAndTermView.as_view(), name="current-session"
    ),
    path("session/list/", SessionListView.as_view(), name="sessions"),
    path("session/create/", SessionCreateView.as_view(), name="session-create"),
    path(
        "session/<int:pk>/update/",
        SessionUpdateView.as_view(),
        name="session-update",
    ),
    path(
        "session/<int:pk>/delete/",
        SessionDeleteView.as_view(),
        name="session-delete",
    ),
    path("term/list/", TermListView.as_view(), name="terms"),
    path("term/create/", TermCreateView.as_view(), name="term-create"),
    path("term/<int:pk>/update/", TermUpdateView.as_view(), name="term-update"),
    path("term/<int:pk>/delete/", TermDeleteView.as_view(), name="term-delete"),
    path("class/list/", ClassListView.as_view(), name="classes"),
    path("class/create/", ClassCreateView.as_view(), name="class-create"),
    path("class/<int:pk>/update/", ClassUpdateView.as_view(), name="class-update"),
    path("class/<int:pk>/delete/", ClassDeleteView.as_view(), name="class-delete"),
    path("subject/list/", SubjectListView.as_view(), name="subjects"),
    path("subject/create/", SubjectCreateView.as_view(), name="subject-create"),
    path(
        "subject/<int:pk>/update/",
        SubjectUpdateView.as_view(),
        name="subject-update",
    ),
    path(
        "subject/<int:pk>/delete/",
        SubjectDeleteView.as_view(),
        name="subject-delete",
    ),
    path('teacher/register/<int:subject_id>/', attendance_register, name='attendance_register'),
    path('get-estado-data/', get_estado_data, name='get_estado_data'),
    path('get-payment-distribution/', get_payment_distribution, name='get_payment_distribution'),
    path('get-kpi-data/', get_kpi_data, name='get_kpi_data'),
    path('global/attendance/', views.admin_attendance_list, name='admin_attendance_list'),
    path('global/class/<int:class_id>/', views.admin_class_details, name='admin_class_details'),

]

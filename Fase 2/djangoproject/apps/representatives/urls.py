from django.urls import path

from .views import (
    RepresentativesCreateView,
    RepresentativesDeleteView,
    RepresentativesDetailView,
    RepresentativesListView,
    RepresentativesUpdateView,
    RepresentativeListView,
    RepresentativeStudentDetailView,
    RepresentativeContentView,
    EventListView,
    RepresentativeAnnotationsView
)

urlpatterns = [
    path("list/", RepresentativesListView.as_view(), name="representatives-list"),
    path("<int:pk>/", RepresentativesDetailView.as_view(), name="representatives-detail"),
    path("create/", RepresentativesCreateView.as_view(), name="representatives-create"),
    path("<int:pk>/update/", RepresentativesUpdateView.as_view(), name="representatives-update"),
    path("<int:pk>/delete/", RepresentativesDeleteView.as_view(), name="representatives-delete"),
    path("representatives/<int:pk>/students/", RepresentativeListView.as_view(), name="representative_student_list"),
    path("representatives/<int:representative_pk>/student/<int:student_pk>/", RepresentativeStudentDetailView.as_view(), name="representative_student_detail"),
    path("representative/<int:pk>/content/", RepresentativeContentView.as_view(), name="representative_content"),
    path("calendar/<int:subject_id>/", EventListView.as_view(), name="representatives_calendar"),
     path('representative/<int:representative_id>/student/<int:student_id>/annotations/', RepresentativeAnnotationsView.as_view(), name='representative_annotation_list'),



]

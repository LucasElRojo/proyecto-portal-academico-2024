from django.urls import path

from .views import (
    RepresentativesCreateView,
    RepresentativesDeleteView,
    RepresentativesDetailView,
    RepresentativesListView,
    RepresentativesUpdateView,
    RepresentativeListView
)

urlpatterns = [
    path("list/", RepresentativesListView.as_view(), name="representatives-list"),
    path("<int:pk>/", RepresentativesDetailView.as_view(), name="representatives-detail"),
    path("create/", RepresentativesCreateView.as_view(), name="representatives-create"),
    path("<int:pk>/update/", RepresentativesUpdateView.as_view(), name="representatives-update"),
    path("<int:pk>/delete/", RepresentativesDeleteView.as_view(), name="representatives-delete"),
    path("<int:representative_id>/students/", RepresentativeListView.as_view(), name="representative_student"),

]

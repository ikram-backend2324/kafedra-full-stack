"""
documents/urls.py
"""
from django.urls import path
from . import views

urlpatterns = [
    path("",                                views.DashboardView.as_view(),      name="dashboard"),
    path("upload/",                         views.UploadView.as_view(),         name="upload"),
    path("documents/<int:pk>/",             views.DocumentDetailView.as_view(), name="document_detail"),
    path("documents/<int:pk>/analyze/",     views.AnalyzeView.as_view(),        name="analyze_document"),
    path("documents/<int:pk>/delete/",      views.delete_document,              name="delete_document"),
]

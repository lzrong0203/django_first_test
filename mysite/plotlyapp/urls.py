from django.urls import path

from . import views

urlpatterns = [
    path("", views.plotly_chart, name="plotly_chart"),
]
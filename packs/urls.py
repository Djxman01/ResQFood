# packs/urls.py
from django.urls import path
from . import views

app_name = "packs"
urlpatterns = [
    path("", views.pack_list, name="list"),   # /packs/
]

# packs/views.py
from django.shortcuts import render

def pack_list(request):
    return render(request, "packs/list.html")

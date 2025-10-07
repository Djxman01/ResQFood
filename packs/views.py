from django.shortcuts import render

def pack_list(request):
    return render(request, "packs/list.html")

def pack_detail(request, pk):
    # solo pasamos el pk; el resto lo trae el fetch a la API
    return render(request, "packs/detail.html", {"pk": pk})

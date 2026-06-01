from django.shortcuts import render


def perfume_list_stub(request):
    return render(request, "catalog/perfume_list.html")


def perfume_detail_stub(request, pk):
    return render(request, "catalog/perfume_detail.html", {"pk": pk})


def collection_list_stub(request):
    return render(request, "collection/list.html")

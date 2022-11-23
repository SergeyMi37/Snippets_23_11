from django.http import Http404
from django.shortcuts import render, redirect
from MainApp.models import Snippet


def index_page(request):
    context = {'pagename': 'PythonBin'}
    return render(request, 'pages/index.html', context)


def add_snippet_page(request):
    if request.method == "GET":
        context = {'pagename': 'Добавление нового сниппета'}
        return render(request, 'pages/add_snippet.html', context)
    elif request.method == "POST":
        # print("form data = ", list(request.POST.items()))
        snippet = Snippet(
            name=request.POST["name"],
            lang=request.POST["lang"],
            code=request.POST["code"]
        )
        snippet.save()
        return redirect("snippets-list")


def snippets_page(request):
    snippets = Snippet.objects.all()
    context = {
        'pagename': 'Просмотр сниппетов',
        'snippets': snippets
    }
    return render(request, 'pages/view_snippets.html', context)


def snippet_detail(request, snippet_id):
    snippet = Snippet.objects.get(id=snippet_id)
    context = {
        'snippet': snippet
    }
    return render(request, 'pages/snippet_detail.html', context)

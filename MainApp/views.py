from django.http import Http404
from django.shortcuts import render, redirect
from MainApp.models import Snippet
from MainApp.forms import SnippetForm, UserRegistrationForm, CommentForm
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.db.models import Count


def index_page(request):
    context = {'pagename': 'PythonBin'}
    return render(request, 'pages/index.html', context)


def add_snippet_page(request):
    if request.method == "GET":
        form = SnippetForm()
        context = {
            'pagename': 'Добавление нового сниппета',
            'form': form
        }
        return render(request, 'pages/add_snippet.html', context)
    elif request.method == "POST":
        form = SnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save(commit=False)
            snippet.user = request.user
            snippet.save()
        return redirect("snippets-list")


def snippets_page(request):
    # Извлекаем query-параметр:
    filter = request.GET.get('filter')
    snippets = Snippet.objects.all()
    pagename = 'Просмотр сниппетов'
    users = User.objects.all().annotate(num_snippets=Count('snippet')).filter(num_snippets__gte=1)
    if filter:
        snippets = snippets.filter(user=request.user)
        pagename = 'Мои сниппеты'

    username = request.GET.get('username')
    if username:
        filter_user = User.objects.get(username=username)
        snippets = snippets.filter(user=filter_user)

    lang = request.GET.get("lang")
    if lang is not None:
        snippets = snippets.filter(lang=lang)

    sort = request.GET.get("sort")
    if sort == 'name':
        snippets = snippets.order_by("name")
        sort = '-name'
    elif sort == '-name' or sort == 'init':
        snippets = snippets.order_by("-name")
        sort = "name"
    if sort is None:
        sort = "init"

    context = {
        'pagename': pagename,
        'snippets': snippets,
        'lang': lang,
        'sort': sort,
        'users': users
    }
    return render(request, 'pages/view_snippets.html', context)


def snippet_detail(request, snippet_id):
    snippet = Snippet.objects.get(id=snippet_id)
    comment_form = CommentForm()
    comments = snippet.comments
    context = {
        'snippet': snippet,
        'comment_form': comment_form,
        'comments': comments,
    }
    return render(request, 'pages/snippet_detail.html', context)


@login_required
def snippet_delete(request, snippet_id):
    snippet = Snippet.objects.get(id=snippet_id)
    if snippet.user != request.user:
        raise PermissionDenied()
    snippet.delete()
    return redirect("snippets-list")


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        # print("username =", username)
        # print("password =", password)
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            print("Success")
        else:
            # Return error message
            pass
    return redirect(request.META.get('HTTP_REFERER', '/'))


def logout_page(request):
    auth.logout(request)
    return redirect(request.META.get('HTTP_REFERER', '/'))


def registration(request):
    if request.method == "GET":
        form = UserRegistrationForm()
        context = {
            'form': form
        }
        return render(request, 'pages/registration.html', context)
    elif request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            context = {
                'form': form
            }
            return render(request, 'pages/registration.html', context)


def comment_add(request):
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        snippet_id = request.POST["snippet_id"]
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.snippet = Snippet.objects.get(id=snippet_id)
            comment.save()
            return redirect("snippet-detail", snippet_id)

    raise Http404

from django.shortcuts import render

# Create your views here.


def index(request):
    context = {}
    return render(request, 'substitute_finder/index.html', context)

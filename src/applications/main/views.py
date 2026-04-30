from django.shortcuts import render, redirect

def home_view(request):
    context = {
        "project":{
            "name": "Duck"
        }
    }
    return render(request, "pages/home/index.html",context)

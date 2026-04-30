from django.shortcuts import render, redirect

def home_view(request):
    context = {
        "project":{
            "name": "Duck"
        }
    }
    return render(request, "pages/home/index.html",context)



def storefront_electronic_section(request):
    return render(request,"pages/home/electronic_section.html")

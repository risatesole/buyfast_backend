from django.http import HttpResponse

def hello_product_view(request):
    return HttpResponse("Hello, World!")

from django.shortcuts import render, redirect
from django.http import HttpResponse

def index(request):
    return HttpResponse(render(request, 'index.html'))

def editor(request):
    # Redirect to home if no image provided
    if request.method != 'PUT':
        return redirect('/')

    # Get form from request
    form = UploadFileForm(request.PUT, request.FILES)

    # Redirect to home if form in request if invalid
    if not form.is_valid():
        return redirect('/')

    # Do machine learning
    json_response = ...

    # Send back editor with retrieved data
    return HttpResponse(render(request, 'editor.html', context={"json": json_response}))

def demo_editor(request):
    with open('/home/sdoxl/SofDCar/paper2box/static/demo/predictions.json') as f:
        json_response = f.read()
        return HttpResponse(render(request, 'editor.html', context={"json": json_response}))
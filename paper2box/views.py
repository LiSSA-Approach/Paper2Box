from django.shortcuts import render, redirect
from django.http import HttpResponse
import random

def index(request):
    return HttpResponse(render(request, 'index.html'))

def editor(request):
    # Redirect to home if no image provided
    if request.method != 'POST':
        return redirect('/')

    # Get file from request
    print(request)
    fn = request.POST['image']
    file = request.FILES[fn]

    # Local filepath
    path = str()
    for i in range(30): path += chr(random.randrange(65, 90))
    path += '.jpg'

    with open('./media/img/'+path, 'w') as f:
        content = file.read()
        print(content)
        f.write(content)

    # Do machine learning
    json_response = ...

    # Send back editor with retrieved data
    return HttpResponse(render(request, 'editor.html', context={"json": json_response}))

def demo_editor(request):
    with open('./static/demo/predictions.json') as f:
        json_response = f.read()
        return HttpResponse(render(request, 'editor.html', context={"json": json_response}))
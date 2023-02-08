from django.shortcuts import render, redirect
from django.http import HttpResponse
import random
from machine_learning.detectron2_wrapper import get_prediction

def index(request):
    return HttpResponse(render(request, 'index.html'))

def editor(request):
        # Redirect to home if no image provided
    if request.method != 'POST' or 'image' not in request.FILES:
        return redirect('/')

    # Get file from request
    file = request.FILES['image']

    path = ''.join([chr(random.range(65, 90)) for i in range(30)])+'.jpg'
    with open('./media/img/'+path, 'w') as f:
        content = file.read()
        print(content)
        f.write(content)

    # Do machine learning
    json_response = get_prediction(path)

    # Send back editor with retrieved data
    return HttpResponse(render(request, 'editor.html', context={"json": json_response}))


def editor_json(request):
    # Redirect to home if no image provided
    if request.method != 'POST':
        return redirect('/')

    json_response = request.POST['json']

    # Send back editor with retrieved data
    return HttpResponse(render(request, 'editor.html', context={"json": json_response}))

def demo_editor(request):
    with open('./static/demo/predictions.json') as f:
        json_response = f.read()
        return HttpResponse(render(request, 'editor.html', context={"json": json_response}))
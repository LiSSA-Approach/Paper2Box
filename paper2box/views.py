from django.shortcuts import render, redirect
from django.http import HttpResponse
import random
from machine_learning.detectron2_wrapper import get_prediction

def index(request):
    return HttpResponse(render(request, 'index.html'))

def editor(request):
    # Redirect to home if no image provided
    if request.method != 'POST':
        return redirect('/')

    # Get file from request
    file = request.FILES['image']

    path = ''.join([chr(random.randrange(65, 90)) for i in range(30)])+'.jpg'
    fpath = './media/img/'+path
    with open(fpath, 'wb') as f:
        content = file.read()
        f.write(content)

    # Do machine learning
    json_response = get_prediction(fpath)

    # Send back editor with retrieved data
    return HttpResponse(render(request, 'editor.html', context={"json": json_response}))

def demo_editor(request):
    with open('./static/demo/predictions.json') as f:
        json_response = f.read()
        return HttpResponse(render(request, 'editor.html', context={"json": json_response}))
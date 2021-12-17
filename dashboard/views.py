from django.shortcuts import render
from .forms import DashboardForm, HomeworkForm, NotesForm,TodoForm, UserRegistrationform
from django.core.checks import messages
from django.shortcuts import redirect, render
from .models import *
from django.views import generic
from django.contrib import messages
from youtubesearchpython import VideosSearch
from django.contrib.auth.decorators import login_required
import requests
import wikipedia
from django.contrib.auth.decorators import login_required

def home(request):
    return render (request,'dashboard/home.html')

@login_required
def notes(request):
    if request.method =="POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
            notes.save()
        messages.success(request,f"Notes added by {request.user} sucessfully")
    else:
        form =NotesForm()
    notes = Notes.objects.filter(user=request.user)
    return render (request,'dashboard/notes.html',{'notes':notes,'form':form,})

@login_required
def delete_note(request,pk):
    note = Notes.objects.get(id=pk)
    note.delete()
    messages.success(request,f"Notes deleted by {request.user} sucessfully")
    return redirect('notes')

@login_required
def note_detail(request,pk):
    note = Notes.objects.get(id=pk)
    return render(request,'dashboard/note-detail.html',{'note':note})

@login_required
def homework(request):
    if request.method =="POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished =='on':
                    finished = True
                else:
                    finished= False
            except:
                finished = False
            homeworks = Homework(user= request.user,
            subject=request.POST['subject'],
            title = request.POST['title'], 
            description = request.POST['description'],
            due = request.POST['due'],
            is_finished = finished
            )
            homeworks.save()
            messages.success(request,f"Homework added by {request.user} sucessfully")
    else:
        form = HomeworkForm()
    homeworks = Homework.objects.filter(user=request.user)
    if len(homeworks)==0:
        homework_done =True
    else:
        homework_done =False
    return render(request,'dashboard/homework.html',{'homeworks':homeworks,'homeork_done':homework_done,'form':form})

@login_required
def update_homework(request,pk):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')

@login_required
def delete_homework(request,pk):
    homework = Homework.objects.get(id=pk)
    homework.delete()
    messages.success(request,f"Homework deleted by {request.user} sucessfully")
    return redirect('homework')


def youtube(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text,limit= 10)
        result_list =[]
        for i in video.result()['result']:
            result_dict ={
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'views':i['viewCount']['short'],
                'published':i['publishedTime'],
            }
            desc =''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc+=j['text']
            result_dict['description'] = desc
            result_list.append(result_dict)
        return render(request,'dashboard/youtube.html',{'form':form,'result_list':result_list})
    else:
        form = DashboardForm()
    return render(request,'dashboard/youtube.html',{'form':form,})

@login_required
def todo(request):
    if request.method=='POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on' :
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            user_todo = Todo(user=request.user,title=request.POST['title'],is_finished = finished )
            user_todo.save()
            messages.success(request,f"Todo added by {request.user} sucessfully")
    else:
        form =TodoForm()
    todos =Todo.objects.filter(user=request.user)
    if len(todos) == 0:
        todo_done = True
    else:
        todo_done =False
    context = {'todos':todos,'form':form,'todo_done':todo_done}
    return render(request,'dashboard/todo.html',context) 

@login_required
def update_todo(request,pk):
    todo =Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished =True
    todo.save()
    return redirect('todo')

@login_required
def delete_todo(request,pk):
    todo = Todo.objects.get(id=pk)
    todo.delete()
    return redirect('todo')


def books(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url)
        answer = r.json()
        result_list =[]
        for i in range(10):
            result_dict ={
               'title':answer['items'][i]['volumeInfo']['title'],
               'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
               'description':answer['items'][i]['volumeInfo'].get('description'),
               'count':answer['items'][i]['volumeInfo'].get('pageCount'),
               'categories':answer['items'][i]['volumeInfo'].get('categories'),
               'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
               'preview':answer['items'][i]['volumeInfo'].get('previewLink'),
               'thumbnail':answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
            }
            result_list.append(result_dict)
        return render(request,'dashboard/books.html',{'form':form,'result_list':result_list})
    else:
        form = DashboardForm()
    return render(request,'dashboard/books.html',{'form':form,})

def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definitions =answer[0]['meanings'][0]['definitions'][0]['definition']
            example = answer[0]['meanings'][0]['definitions'][0]['example']
            synonyms =answer[0]['meanings'][0]['definitions'][0]['synonyms']
            context ={
                'form':form,
                'input':text,
                'phonetics':phonetics,
                'audio':audio,
                'definition':definitions,
                'example':example,
                'synonyms':synonyms,
            }
        except:
             context={
                    'form':form,
                    'input':''
                }
        return render(request,'dashboard/dictionary.html',context)
    else:
        form = DashboardForm()
        context ={'form':form,}
    return render(request,'dashboard/dictionary.html',context,)

def wiki(request):
    if request.method == "POST":
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context ={
            'form': form,
            'title':search.title,
            'link':search.url,
            'details':search.summary,
        }
        return render(request,'dashboard/wiki.html',context)
    else:
        form = DashboardForm()
    return render(request,'dashboard/wiki.html',{'form':form},)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationform(request.POST)
        if form.is_valid():
            form.save()
            username =form.cleaned_data.get('username')
            messages.success(request,f"Accounted created for {username} sucessfully")
            return redirect('login')
    else:
         form = UserRegistrationform()
    context ={'form':form,}
    return render(request,'dashboard/register.html',context)

def profile(request):
    homeworks = Homework.objects.filter(is_finished=False,user=request.user)
    todos = Todo.objects.filter(is_finished=False,user=request.user)
    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done =False
    if len(todos) == 0:
        todo_done= True
    else:
        todo_done =False 
    context = {
        'homeworks':homeworks,
        'todos':todos,
        'homework_done':homework_done,
        'todo_done':todo_done,
    }
    return render(request,'dashboard/profile.html',context)
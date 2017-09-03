from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import  login_required
from sign.models import  Event,Guest
from django.core.paginator import  Paginator,EmptyPage,PageNotAnInteger
from django.shortcuts import  render,get_object_or_404

# Create your views here.
def index(request):
    return render(request,'index.html')


def login_action(request):
    if request.method == 'POST':
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        user =auth.authenticate(username=username,password=password)
        # if username=='admin' and password=='12345' :
        if user is not None:
            auth.login(request,user)
            # response = HttpResponseRedirect('/event_manage/')
            #response.set_cookie('user',username,3600)
            request.session['user'] = username
            response = HttpResponseRedirect('/event_manage/')

            return response
        else:
            return render(request,'index.html',{'error':'username or password wrong'})
@login_required
def event_manage(request):
    # username = request.COOKIES.get('user','')
    events= Event.objects.all()
    username = request.session.get('user','')
    return  render(request,"event_manage.html",{'user':username,'events':events})

@login_required
def search_name(request):
    username = request.session.get('user','')
    search_name = request.GET.get('name','')
    event_list = Event.objects.filter(name__contains=search_name)
    return render(request,'event_manage.html',{'user':username,'events':event_list})

@login_required
def guest_manage(request):
    # username = request.COOKIES.get('user','')
    guests= Guest.objects.all()
    username = request.session.get('user','')

    pageinator = Paginator(guests,2)
    page =request.GET.get('page')
    try:
        contacts = pageinator.page(page)
    except PageNotAnInteger:
        contacts = pageinator.page(1)
    except EmptyPage:
        contacts = Paginator.page(pageinator.num_pages)



    return  render(request,"guest_manage.html",{'user':username,'guests':contacts})

@login_required
def sign_index(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'sign_index.html', {'event': event})


@login_required
def sign_index_action(request,event_id):
    event = get_object_or_404(Event, id=event_id)
    phone = request.POST.get('phone','')
    result = Guest.objects.filter(phone = phone)
    if not result:
        return render(request, 'sign_index.html', {'event': event,
        'hint': 'phone error.'})
    result = Guest.objects.filter(phone=phone,event_id=event_id)
    if not result:
        return render(request, 'sign_index.html', {'event': event,
        'hint': 'event id or phone error.'})
    result = Guest.objects.get(phone=phone,event_id=event_id)
    if result.sign:
        return render(request, 'sign_index.html', {'event': event,
        'hint': "user has sign in."})
    else:
        Guest.objects.filter(phone=phone,event_id=event_id).update(sign = '1')
        return render(request, 'sign_index.html', {'event': event,
        'hint':'sign in success!',
        'guest': result})

@login_required
def logout(request):
    auth.logout(request)
    response = HttpResponseRedirect('/index/')
    return response

from django.shortcuts import render,HttpResponse,render_to_response
from django.template.loader import render_to_string

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Property, Visitor, Owner, Rented, Review, User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
import json 
from django.http import HttpResponse
# from django.views import View
from django.template.loader import render_to_string


def login_user(request):
    error = None
    if(request.method == "POST"):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username, password = password)
        if user is not None:
            login(request, user)
            current_user = request.user
            if(current_user.is_owner):
                return redirect("ownerdashboard")
            else:
                return redirect("visitordashboard")
        else:
            error = "Invalid credentials. Try again."
    return render(request, "login.html", {'error':error})

@login_required
def ownerdashboard(request):
    if request.method == 'GET':
        if 'addProperties' in request.path:
            return render(request,'addProperty.html',{})        
        current_user = request.user
        current_owner = Owner.objects.get(user = current_user)
        tenants = Rented.objects.filter(owner_id = current_owner)
        properties = Property.objects.filter(owner = current_owner)  
        paginator = Paginator(properties, 2)
        page = request.GET.get('page')
        try:
            property_disp = paginator.page(page)
        except PageNotAnInteger:
            property_disp = paginator.page(1)
        except EmptyPage:
            property_disp = paginator.page(paginator.num_pages)

        html = render_to_string('owner_dashboard.html', {'properties': property_disp,'user':current_user})
        return HttpResponse(html)

    if request.method == 'POST':
        current_user = request.user
        if(current_user.is_owner):
            current_owner = Owner.objects.get(user = current_user) 
            description = request.POST['description']
            price = request.POST['price']
            location = request.POST['location']
            if request.FILES:
                image = request.FILES['image']
            else:
                image = None
            new_prop = Property.objects.create(owner = current_owner, description=description,price=price,location=location,image=image)
            new_prop.save()
            return HttpResponse({'status':'success'})        
          
@login_required
def editProperties(request,pk):
    if request.method == 'GET':
        if pk:
            properties = Property.objects.get(id = pk)  
            return render(request,'addProperty.html',{'data':properties, 'pk': pk})
    if request.method == 'POST':
        current_user = request.user
        if(current_user.is_owner):
            current_owner = Owner.objects.get(user = current_user) 
            description = request.POST['description']
            price = request.POST['price']
            location = request.POST['location']
            edit_prop = Property.objects.get(id = pk)
            edit_prop.description = description
            edit_prop.price = price
            edit_prop.location = location
            if request.FILES:
                edit_prop.image = request.FILES['image']
            edit_prop.save()
            return HttpResponse({'status':'success'}) 

@login_required
def deleteProperties(request, pk):
    current_user = request.user
    if(current_user.is_owner):
        current_owner = Owner.objects.get(user = current_user)             
        del_prop = Property.objects.get(id = pk)
        del_prop.delete()           
        return redirect("ownerdashboard")  


@login_required
def visitordashboard(request):
    properties = Property.objects.all() 
    paginator = Paginator(properties, 5)
    page = request.GET.get('page')
    try:
        property_disp = paginator.page(page)
    except PageNotAnInteger:
        property_disp = paginator.page(1)
    except EmptyPage:
        property_disp = paginator.page(paginator.num_pages)   
    
    return render(request, "visitor_dashboard.html", {"properties": property_disp})


@login_required
def bookproperty(request, id):
    prop = Property.objects.get(id=id)
    visitor = Visitor.objects.get(user=request.user)
    prop.availability = False
    prop.visitor_id = visitor
    prop.save()
    return redirect('visitordashboard')


def register(request):
    error = None
    if (request.method =="POST"):
        username = request.POST['username']
        password = request.POST['password']
        name = request.POST['name']
        existing = User.objects.filter(username__iexact=username)        
        if existing.exists():
            error = "This username already exists. Kindly provide another username."
        new_user = User.objects.create_user(username = username, password = password, is_owner = True)
        new_user.save()
        new_owner = Owner.objects.create(user = new_user, owner_name = name, num_properties = 0)
        new_owner.save()
        return redirect('login')
    return render(request, "register.html",{'error':error})



def register_visitor(request):
    error = None
    if (request.method =="POST"):
        username = request.POST['username']
        password = request.POST['password']
        profile = request.POST['profile']
        pref_location = request.POST['pref_location']
        existing = User.objects.filter(username__iexact=username)
        if existing.exists():
            error = "This username already exists. Kindly provide another username."
            return render(request, "register_visitor.html",{'error':error})
        new_user = User.objects.create_user(username = username, password = password, is_owner = False)
        new_user.save()
        new_visitor = Visitor.objects.create(user = new_user, profile = profile, pref_location = pref_location)
        new_visitor.save()
        return redirect('login')
    else:
        return render(request, "register_visitor.html",{})
    

def logout_user(request):
    logout(request)
    return redirect("/")


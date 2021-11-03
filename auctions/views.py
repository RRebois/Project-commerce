from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
import datetime

from .models import *
from .forms import *

def func():
    category
    listings = listing.objects.all().order_by('item')
    return listings

def index(request):
    listing=func()
    item_Not_On_Fire = itemToSell.objects.filter(onFire = 'False')
    item_On_Fire = itemToSell.objects.filter(onFire = 'True')
    return render(request, "auctions/index.html", {
        "listing": listing,
        "itemNoF": item_Not_On_Fire,
        "itemoF": item_On_Fire
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        price = request.POST["price"]
        username = request.user.id

        image_url = request.POST["image_url"]

        print(f"username:{username}")
        # Try finding the category id from the submitted form data if any selected
        try:
            category_id = category.objects.get(category=request.POST["category"]).id
            newItem = itemToSell.objects.create(title=title, description=description, user=User.objects.get(pk=username), 
                    category=category.objects.get(pk=category_id), image_url=image_url)
            #print(f"category:{category_id}")
        except ObjectDoesNotExist:
            newItem = itemToSell.objects.create(title=title, description=description, user=User.objects.get(pk=username), 
                    image_url=image_url)
            #print(f"category:{category_id}")
        
        newprice = bid.objects.create(price=price, item=itemToSell.objects.all().last(), userSelling=User.objects.get(pk=username))
        newListing = listing.objects.create(item=itemToSell.objects.all().last(), bid=bid.objects.all().last())

        messages.success( request, 'Your item has been successfully added to the listing.')
        return HttpResponseRedirect(reverse("itemPage", args=(title,)))
    
    categories = category.objects.all()
    return render(request, "auctions/create.html", {
        "form": newListingForm(),
        "categories": categories
    })

def itemPage(request, word):
    itemTitle=itemToSell.objects.get(title=word)

    try:
        coms=comment.objects.get(item=itemTitle.id)
    except ObjectDoesNotExist:
        return render(request, "auctions/itemPage.html", {
        "item": itemTitle
        })

    return render(request, "auctions/itemPage.html", {
        "item": itemTitle,
        "comment": coms
    })
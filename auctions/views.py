from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

import datetime

from .models import *
from .forms import *

def index(request):
    listings=listing.objects.filter(active='True').order_by('item')
    itemSelected=itemToSell.objects.all()
    itemOF=itemToSell.objects.filter(onFire='True')
    itemNOF=itemToSell.objects.filter(onFire = 'False')

    return render(request, "auctions/index.html", {
        "listing": listings,
        "itemSelected": itemSelected,
        "itemOF": itemOF,
        "itemNOF": itemNOF
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

@login_required(login_url='login') #@login_required empêche les personnes non connectés d'acceder à la page demandés
def create(request): #login_url permet de redigirer vers une autre url, ici on redirige vers la page de connexion login
    if request.method == "POST":

        # Take in the data the user submitted and save it as form
        dataForm = newListingForm(request.POST)
        # Check if form data is valid (server-side)
        if dataForm.is_valid():
            # Isolate the task from the 'cleaned' version of form data
            title = dataForm.cleaned_data["title"]
            description = dataForm.cleaned_data["description"]
            price = dataForm.cleaned_data["price"]
            username = request.user.id

            image_url = dataForm.cleaned_data["image_url"]

            # print(f"username:{username}")
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
            
            newprice = bid.objects.create(price=price, item=itemToSell.objects.get(pk=newItem.id), userSelling=User.objects.get(pk=username))
            newListing = listing.objects.create(item=itemToSell.objects.get(pk=newItem.id), bid=bid.objects.get(pk=newprice.id))

            messages.success(request, 'Your item has been successfully added to the listing.')
            return HttpResponseRedirect(reverse("itemPage", args=(newItem.id, title)))
    
    categories = category.objects.all()
    return render(request, "auctions/create.html", {
        "form": newListingForm(),
        "categories": categories
    })

@login_required(login_url='login')
def itemPage(request, item_id, word):
    if request.method == "POST":

        # Get the title of the listing item:
        title=itemToSell.objects.get(pk=item_id)

        bids = bid.objects.get(item=item_id)

        if 'watchlist' in request.POST:
            watch = watchlist.objects.get(item=itemToSell.objects.get(pk=item_id), user=User.objects.get(pk=request.user.id))
            if watch.watch:
                watch.watch = "False"
                watch.save()
                messages.success(request, 'Item removed from watchlist.')
                return HttpResponseRedirect(reverse("itemPage", args=(item_id, title)))
            else:
                watch.watch = "True"
                watch.save()
                messages.success(request, 'Item added to watchlist.')
                return HttpResponseRedirect(reverse("itemPage", args=(item_id, title)))

        # To add a new comment:
        if 'addComment' in request.POST:
            # Take in the data the user submitted and save it as form
            dataComment = addCommentForm(request.POST)
            # Check if form data is valid (server-side)
            if dataComment.is_valid():
                # Isolate the task from the 'cleaned' version of form data
                Comment = dataComment.cleaned_data["comment"]
                print(f"{Comment}")
                
                # Add the comment into the database:
                newComment = comment.objects.create(comment=Comment, user=User.objects.get(pk=request.user.id), 
                    item=itemToSell.objects.get(pk=item_id))

        # To make a bid:
        if 'makeBid' in request.POST:
            # Take in the data the user submitted and save it as form
            dataBid = bidForm(request.POST)
            # Check if form data is valid (server-side)
            if dataBid.is_valid():
                # Isolate the task from the 'cleaned' version of form data
                newBid = dataBid.cleaned_data["bid"]
                
                # Get the initial and current prices:
                initialPrice=bids.price
                currentPrice=bids.current

                if not currentPrice:
                    if newBid < initialPrice.amount:
                        messages.warning(request, 'Error: The minimum bid must match the initial price.')
                        return HttpResponseRedirect(reverse("itemPage", args=(item_id, title)))
                
                    bids.current=newBid
                    bids.userWinning=User.objects.get(pk=request.user.id)
                    bids.count = bids.count + 1 
                    bids.save()

                    messages.success(request, 'Bid placed successfully. Good luck!')
                    return HttpResponseRedirect(reverse("itemPage", args=(item_id, title)))

                else:
                    if newBid <= currentPrice.amount:
                        messages.warning(request, 'Error: Your bid must be higher.')
                        return HttpResponseRedirect(reverse("itemPage", args=(item_id, title)))

                    bids.current=newBid
                    bids.userWinning=User.objects.get(pk=request.user.id)
                    bids.count = bids.count + 1 
                    bids.save()

                    if bids.count > 5:
                        #newItemOF=listing.objects.get(item=itemToSell.objects.get(pk=item_id))
                        #newItemOF.onFire ="True"
                        #newItemOF.save()
                        title.onFire = "True"
                        title.save()

                    messages.success(request, 'Bid placed successfully. Good luck!')
                    return HttpResponseRedirect(reverse("itemPage", args=(item_id, title)))

        # To close the current auction
        if 'close' in request.POST:
            listings = listing.objects.get(item=item_id)
            listings.active = "False"
            listings.save()
            #print(f"The title sent is: {word} and the id is {title_id}")

            if bids.current:
                messages.success(request, 'You successfully closed your auction and sold your item, Congratulations!!!')
                return HttpResponseRedirect(reverse("itemPage", args=(item_id, title)))
            else:
                messages.success(request, 'You successfully closed your auction.')
                return HttpResponseRedirect(reverse("itemPage", args=(item_id, title)))

    itemTitle=itemToSell.objects.get(pk=item_id)
    bidTitle=bid.objects.get(item=item_id)
    listings=listing.objects.get(item=item_id)
    allCommentaries = comment.objects.filter(item=item_id)

    try:
        watch = watchlist.objects.get(item=itemToSell.objects.get(pk=item_id), user=User.objects.get(pk=request.user.id))
    except ObjectDoesNotExist:
        watch = watchlist.objects.create(item=itemToSell.objects.get(pk=item_id), user=User.objects.get(pk=request.user.id))

    return render(request, "auctions/itemPage.html", {
        "item": itemTitle,
        "bid": bidTitle,
        "bidForm": bidForm(),
        "listing": listings,
        "watch": watch,
        "comments": allCommentaries,
        "addCommentForm": addCommentForm
    })

@login_required(login_url='login')
def watchedItems(request, username):

    # Select all items being watch for the logged user (watch='True'):
    watchItems = watchlist.objects.filter(watch='True', user = User.objects.get(pk=request.user.id))
    
    # Select all active listing items:
    opened = listing.objects.filter(active = 'True')

    # Select all inactive listing items:
    closed = listing.objects.filter(active = 'False')

    # Select all items:
    itemSold = itemToSell.objects.all()

    for item in itemSold:
        for active in opened:
            if item.id == active.item.id:   
                for watchItem in watchItems:
                    if item.id == watchItem.item.id and watchItem.watch:
                        pass 

    for item in itemSold:
        for close in closed:
            if item.id == close.item.id:   
                for watchItem in watchItems:
                    if item.id == watchItem.item.id and watchItem.watch:
                        pass  
    
    return render(request, "auctions/watchlist.html", {
        "watches": watchItems,
        "opened": opened,
        "closed": closed,
        "itemSold": itemSold
    })

@login_required(login_url='login')
def listingCategory(request):
    categories=category.objects.all()
    return render(request, "auctions/listingCategory.html", {
        "categories": categories
        })

@login_required(login_url='login')
def categoryPage(request, word):
    if request.method =="POST":

        #Select the category id and select all items that belong to that category
        categorySelected=category.objects.get(category=word).id 
        itemSelected=itemToSell.objects.filter(category=categorySelected)
        print(f"{itemSelected}")
        
        #Select the listing of all objects selected before:
        listings=listing.objects.filter(active='True').order_by('item')

        return render(request, "auctions/categoryPage.html", {
            "listing": listings,
            "itemSelected": itemSelected
        })
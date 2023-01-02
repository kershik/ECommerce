from sre_parse import CATEGORIES
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Comment, Category

from django import forms

class NewBidForm(forms.Form):
    bid = forms.DecimalField(decimal_places=2, label='')

class NewListingForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput())
    description = forms.CharField(widget=forms.Textarea())
    current_price = forms.DecimalField(max_digits=10, decimal_places=2, label='Starting price', widget=forms.NumberInput())
    photo = forms.ImageField(widget=forms.FileInput(attrs={'required': False,}))

    def __init__(self, *args, **kwargs):
        super(NewListingForm, self).__init__(*args, **kwargs)
        choices = [('','Select Category')] + list(Category.objects.values_list('id', 'name'))
        self.fields['category'] = forms.ChoiceField(choices=choices, required=False, widget=forms.Select())
        for v in self.visible_fields():
            v.field.widget.attrs['class'] = 'form-control'

class NewCommentForm(forms.Form):
    comment = forms.CharField(max_length=200, label="", widget=forms.TextInput(attrs={'class':'comment'}))

def index(request):
    message = "Sorry, there are no active listings."
    return render(request, "auctions/index.html", {
        "title": "Active Listings",
        "listings": Listing.objects.filter(closed=False),
        "message": message
    })

def listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    message = None # for bids less than price
    bids_count = listing.bids.count()
    if bids_count > 0:
        current_user = listing.bids.get(price=listing.current_price).user
    else: 
        current_user = None

    # DO SOMETHING NOT SO UBOGOE
    if listing.closed == True:
        if request.user == listing.creator:
            message = "You closed this listing!"
        else:
            message = "Sorry, this listing was closed by the owner!"
        return render(request, "auctions/close.html", {
            "message": message,
            "win": current_user
        })
        
    if request.method == "POST":
        if 'newbid' in request.POST:
            form = NewBidForm(request.POST)
            if form.is_valid():
                new_bid = form.cleaned_data['bid']
                if new_bid > listing.current_price:
                    bid = Bid(user=request.user, listing=listing, price=new_bid)
                    bid.save()
                    listing.current_price = new_bid
                    listing.save()
                    return HttpResponseRedirect(reverse('listing', args=[listing.id]))
                else:
                    message = "Sorry, your bid must be higher than the current price!"
        if 'close' in request.POST:
            listing.closed = True
            listing.users.remove(request.user)
            listing.save()
            return HttpResponseRedirect(reverse('listing', args=[listing.id]))
        if 'add_watchlist' in request.POST:
            listing.users.add(request.user)
            listing.save()
            return HttpResponseRedirect(reverse('listing', args=[listing.id]))
        if 'remove_watchlist' in request.POST:
            listing.users.remove(request.user)
            listing.save()
            return HttpResponseRedirect(reverse('listing', args=[listing.id]))
        if 'newcomment' in request.POST:
            form = NewCommentForm(request.POST)
            if form.is_valid():
                c = Comment(user=request.user, listing=listing, text=form.cleaned_data['comment'])
                c.save()
                return HttpResponseRedirect(reverse('listing', args=[listing.id]))
    
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids_count": bids_count,
        "current_user": current_user,
        "bid_form": NewBidForm(),
        "message": message,
        "comment_form": NewCommentForm(),
        "comments": listing.comments.all(),
        "watch_users": listing.users.all()
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

@login_required
def create(request):
    if request.method == "POST":
        form = NewListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing_data = form.cleaned_data
            try:
                listing_photo = request.FILES['photo']
            except:
                listing_photo = None
            category = Category.objects.get(id=listing_data['category']) if listing_data['category'] else None
            l = Listing(
                title=listing_data['title'],
                description=listing_data['description'],
                current_price=listing_data['current_price'],
                photo=listing_photo,
                creator=request.user,
                category=category
                )
            l.save()
            return HttpResponseRedirect(reverse('listing', args=[l.id]))
    return render(request, "auctions/create.html", {
        "form": NewListingForm()
    })

@login_required
def watchlist(request):
    message = "There are no active listings in your watchlist yet."
    return render(request, "auctions/index.html", {
        "title": "Watchlist",
        "listings": request.user.watch_listings.filter(closed=False),
        "message": message
    })

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })

def category(request, category_name):
    category = Category.objects.get(name=category_name)
    message = "Sorry, there are no active listing in this category yet."
    return render(request, "auctions/index.html", {
        "title": category_name,
        "listings": Listing.objects.filter(category=category, closed=False), 
        "message": message
    })
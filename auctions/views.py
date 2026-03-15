from decimal import Decimal, InvalidOperation
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import User, Category, Listing, Bid, Comment


@login_required
def listing(request, id):
    listing = get_object_or_404(Listing, pk=id)
    comments = listing.comments.all().order_by("-created_at")
    bids = listing.bids.all().order_by("-amount")
    highest_bid = bids.first()

    # calculate current price
    current_price = highest_bid.amount if highest_bid else listing.starting_bid

    error = None

    # If the user submits a bid
    if request.method == "POST":
        bid_amount = None
        try:
            bid_amount = Decimal(request.POST.get("bid"))
        except (InvalidOperation, TypeError):
            error = "Invalid bid amount."

        # Creating a bid object to save to database
        if bid_amount and not error:
            if bid_amount > Decimal("9999999999.99"):
                error = "Bid amount cannot be greater than $9999999999.99."
            elif bid_amount > current_price:
                Bid.objects.create(
                    listing=listing,
                    bidder=request.user,
                    amount=bid_amount
                )
                return HttpResponseRedirect(reverse("listing", args=[listing.id]))
            else:
                error = "Bid must be $0.10 higher than current price."

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids": bids,
        "current_price": current_price,
        "error": error,
        "comments": comments
    })


@login_required
def comments(request, id):
    listing = get_object_or_404(Listing, pk=id)

    # Get comments fom the listing
    if request.method == "POST":
        comment_data = request.POST.get("comment")

        # Creating a comment object to save to database
        Comment.objects.create(
            listing=listing,
            Username=request.user,
            text=comment_data
        )
        return HttpResponseRedirect(reverse("listing", args=[listing.id]))

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments
    })


def all_listings(request):
    category = request.GET.get("category")
    all_listings = Listing.objects.all()

    # Filtering all listings by category
    if category:
        all_listings = all_listings.filter(category__name=category)
    allcategories = Category.objects.all()
    return render(request, "auctions/all_listing.html", {
        "categories": allcategories,
        "all_listings": all_listings
    })


def closed_listings(request):
    category = request.GET.get("category")

    # Get closed Listings
    closed_listings = Listing.objects.filter(active=False)

    # Calculating current price for each listing
    for listing in closed_listings:
        highest_bid = listing.bids.order_by("-amount").first()
        listing.current_price = highest_bid.amount if highest_bid else listing.starting_bid

    # Filtering the closed listing by category
    if category:
        closed_listings = closed_listings.filter(category__name=category)
    allcategories = Category.objects.all()
    return render(request, "auctions/closed_listing.html", {
        "categories": allcategories,
        "closed_listings": closed_listings
    })


def index(request):
    category = request.GET.get("category")
    activeListings = Listing.objects.filter(active=True).order_by("-created_at")

    # Calculating current price for each listing
    for listing in activeListings:
        highest_bid = listing.bids.order_by("-amount").first()
        listing.current_price = highest_bid.amount if highest_bid else listing.starting_bid

    if category:
        activeListings = activeListings.filter(category__name=category)
    allcategories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": activeListings,
        "categories": allcategories
    })


def categories(request):
        allcategories = Category.objects.all()
        return render(request, "auctions/categories.html", {
            "categories": allcategories
        })

def items(request,id):
    category = get_object_or_404(Category, pk=id)
    items = Listing.objects.filter(category=category)

    for listing in items:
        highest_bid = listing.bids.order_by("-amount").first()
        listing.current_price = highest_bid.amount if highest_bid else listing.starting_bid

    return render(request, "auctions/items.html", {
        "items": items,
        "category": category
    })


@login_required
def toggle_watchlist(request, id):
    listing = get_object_or_404(Listing, pk=id)
    user = request.user

    # If the user already has this listing in their watchlist, remove it
    if listing in user.watchlist.all():
        listing.watchlist.remove(user)
    else:
        listing.watchlist.add(user)

    return HttpResponseRedirect(reverse("listing", args=[listing.id]))


@login_required
def view_watchlist(request):
    user = request.user

    # All listings this user is watching
    watchlist_listings = user.watchlist.all()

    return render(request, "auctions/watchlist.html", {
        "watchlist_listings": watchlist_listings
    })


def create_listing(request):
    if request.method == "GET":
        categories = Category.objects.all()
        return render(request, "auctions/create_listing.html", {
            "categories": categories
        })

    else:
        # Get the data for the filled form #
        title = request.POST.get("title")
        description = request.POST.get("description")
        starting_bid = request.POST.get("starting_bid")
        image_url = request.POST.get("image_url")
        category = request.POST.get("category")
        category_ = get_object_or_404(Category, name=category)

        # request the owner of the lisitng #
        currentUser = request.user

        # create a Lisiting object#
        new_listing = Listing(
            title=title,
            description=description,
            starting_bid=Decimal(starting_bid),
            image_url=image_url,
            category=category_,
            owner=currentUser
        )

        # Save to database#
        new_listing.save()

        # redirect to index#
        return HttpResponseRedirect(reverse("index"))


@login_required
def close_auction(request, id):
    listing = get_object_or_404(Listing, pk=id)
    if request.user == listing.owner:
        listing.active = False
        highest_bid = listing.bids.all().order_by("-amount").first()
        if highest_bid:
            listing.winner = highest_bid.bidder
        listing.save()
    return HttpResponseRedirect(reverse("index"),)


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
        username = request.POST.get("username")
        email = request.POST.get("email")

        # Ensure password matches confirmation
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")
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

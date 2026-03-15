from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=15, decimal_places=2)
    image_url = models.URLField(blank=True,null=True)
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,blank=True, null=True, related_name="listings")
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")
    winner = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="wins")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE,  related_name="bids")
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.bidder} bid {self.amount} on {self.listing}"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    Username = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(null=True,)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.Username} on {self.listing}"

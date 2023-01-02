from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=100)

class Listing(models.Model):
    ''' attr: title, description, current price (bid?), 
    photo, details, closed (t/f) '''
    
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=500)
    current_price = models.DecimalField(max_digits=10, decimal_places=2) # save in place (only price or bid_id?) or make query every time?
    creator = models.ForeignKey(User, related_name="created_listings", on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name="watch_listings")
    photo = models.ImageField(upload_to='auctions', default=None)
    category = models.ForeignKey(Category, related_name="listings", on_delete=models.CASCADE, blank=True, null=True)
    closed = models.BooleanField(default=False)

class Bid(models.Model):
    ''' attrs: listing (foreign), user (foreign), price'''
    listing = models.ForeignKey(Listing, related_name='bids', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='bids', on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Comment(models.Model):
    ''' attrs: listing (foreign), user (foreign), text'''
    listing = models.ForeignKey(Listing, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)

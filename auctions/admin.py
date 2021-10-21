from django.contrib import admin
from .models import *

class userAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "first_name", "last_name")

class categoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category")

class itemAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "title", "user", "image_url")

class watchlistAdmin(admin.ModelAdmin):
    list_display = ("id", "item_id", "watch", "user")

class bidAdmin(admin.ModelAdmin):
    list_display = ("id", "price", "userSelling", "current", "userWinning", "item", "count")

class commentAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "user", "comment", "datePosted")

# Register your models here.
admin.site.register(User, userAdmin)
admin.site.register(itemToSell, itemAdmin)
admin.site.register(category, categoryAdmin)
admin.site.register(watchlist, watchlistAdmin)
admin.site.register(bid, bidAdmin)
admin.site.register(comment, commentAdmin)
admin.site.register(listing)
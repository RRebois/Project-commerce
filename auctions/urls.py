from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("auction<int:item_id>:<str:word>", views.itemPage, name="itemPage"),
    path("<str:username>/watchlist", views.watchedItems, name="watchedItems"),
]

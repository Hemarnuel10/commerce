from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("listing/<int:id>/", views.listing, name="listing"),
    path("closed_listings/", views.closed_listings, name="closed_listings"),
    path("all_listings/", views.all_listings, name="all_listings"),
    path("categories/", views.categories, name="categories"),
    path("categories/<int:id>/", views.items, name="items"),
    path("watchlist/", views.view_watchlist, name="watchlist"),
    path("watchlist/toggle/<int:id>/", views.toggle_watchlist, name="toggle_watchlist"),
    path("listing/<int:id>/close/", views.close_auction, name="close_auction"),
    path("listing/<int:id>/comments/", views.comments, name="comments")
]

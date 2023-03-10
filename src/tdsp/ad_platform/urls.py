from django.urls import path
from .api.bid import BidView
from .api.configure import ConfigurationView
from .api.notify import NotifyView

urlpatterns = [
    path('rtb/bid/', BidView.as_view()),
    path('rtb/notify/', NotifyView.as_view()),
    path('game/configure/', ConfigurationView.as_view()),
]

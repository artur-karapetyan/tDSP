#
from django.urls import path

#
from .api.bid import BidView
from .api.notify import NotifyView
from .api.creatives import CreativeView
from .api.configure import ConfigurationView

urlpatterns = [
    path('rtb/bid/', BidView.as_view()),
    path('rtb/notify/', NotifyView.as_view()),
    path('game/configure/', ConfigurationView.as_view()),
    path('creatives/<str:name>', CreativeView.as_view()),
]

#
from django.urls import path

#
from .api.bid import BidView
from .api.bid_request import BidRequestView
from .api.bid_response import BidResponseView
from .api.category import CategoryView
from .api.login import GenericUserView
from .api.notify import NotifyView
from .api.campaign import CampaignView
from .api.creatives import CreativeView
from .api.configure import ConfigurationView

urlpatterns = [
    path('rtb/bid/', BidView.as_view()),
    path('rtb/notify/', NotifyView.as_view()),
    path('game/configure/', ConfigurationView.as_view()),
    path('api/creatives/<str:creative_id>', CreativeView.get_image),
    path('api/creatives/', CreativeView.as_view()),
    path('api/creatives/<int:page>/', CreativeView.as_view()),
    path('api/campaigns/', CampaignView.as_view()),
    path('api/campaigns/<int:campaign_id>/', CampaignView.as_view()),
    path('api/bid_request/<int:page>/', BidRequestView.as_view()),
    path('api/bid_response/<int:page>/', BidResponseView.as_view()),
    path('api/categories/<int:page>/', CategoryView.get_page),
    path('api/categories/', CategoryView.as_view()),
    path('api/notify/<int:page>/', NotifyView.as_view()),
    path('login/', GenericUserView.login),
    path('logout/', GenericUserView.logout),
]

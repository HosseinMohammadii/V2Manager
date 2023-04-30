from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view),
    path("land/<str:id>/", views.FirstPage.as_view()),
    path("land/<str:id>/info/", views.Info.as_view()),
    path("land/<str:id>/confs/", views.Confs.as_view()),

]

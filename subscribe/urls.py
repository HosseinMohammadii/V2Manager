from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.Dashboard.as_view()),
    path("login/", views.login_view),
    path("logout/", views.logout_view),
    path("land/<str:id>/", views.FirstPage.as_view()),
    path("land/<str:id>/info/", views.Info.as_view()),
    path("land/<str:id>/confs/", views.Confs.as_view()),
    path("repeated-configs/", views.repeated_config_ids),

]


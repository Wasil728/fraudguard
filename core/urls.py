# the normal pages
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("login/",           auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/",          auth_views.LogoutView.as_view(),                          name="logout"),
    path("",                 views.dashboard,    name="dashboard"),
    path("simulator/",       views.simulator,    name="simulator"),
    path("alerts/",          views.alerts_page,  name="alerts"),
    path("alerts/<int:pk>/", views.alert_detail, name="alert_detail"),
    path("analytics/",       views.analytics,    name="analytics"),
    path("settings/",        views.settings_page, name="settings"),
]

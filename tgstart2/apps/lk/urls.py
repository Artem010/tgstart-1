from django.shortcuts import render

# Create your views here.
from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static

from django.urls import include
# import urls

urlpatterns = [
	# path('', views.index, name = 'index'),
	# path('dashboard', views.dashboard, name = 'dashboard')
	path('dashboard/', views.dashboard, name = 'dashboard'),
	path('profile/', views.profile, name = 'profile'),
	path('mybots/', views.mybots, name = 'mybots'),
	path('mybots/removebot', views.removebot, name = 'removebot'),
	path('mybots/activatebot', views.activatebot, name = 'activatebot'),
	path('mybots/deactivatebot', views.deactivatebot, name = 'deactivatebot'),
	path('mybots/edit', views.edit, name = 'edit'),
	path('users/', views.users, name = 'users'),
	path('instruction/', views.instruction, name = 'instruction')
]

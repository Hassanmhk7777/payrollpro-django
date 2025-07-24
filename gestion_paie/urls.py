from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('paie.urls')),
       path('login/', auth_views.LoginView.as_view(template_name='paie/connexion_simple.html'), name='login'),  # ← UTILISER TON TEMPLATE EXISTANT
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
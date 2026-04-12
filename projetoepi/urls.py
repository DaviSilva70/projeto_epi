from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from epi import views as epi_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("epi.urls")),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(
            template_name="login.html", redirect_authenticated_user=True
        ),
        name="login",
    ),
    path("accounts/logout/", epi_views.logout_view, name="logout"),
    path("accounts/register/", epi_views.register, name="register"),
    path("accounts/profile/", epi_views.home, name="profile"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

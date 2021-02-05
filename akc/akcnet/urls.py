from django.urls import path
from . import views

urlpatterns = [
    path("", views.main),
    path("konu/<int:id>", views.konu),
    path("konuac/", views.konuac),
    path("konuac/konuac1", views.konuac1),
    path("konu/<int:id>/yorumyap1", views.yorumyap1),
    path("konu/<int:id>/yorumyap1/<int:sira>", views.yanityap1),
    path("yanitla", views.yanitla),
    path("kaydol", views.kaydol),
]

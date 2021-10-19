from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    # Camera Integration
    path("test", views.test, name='test'),
    path("video_feed/<int:loc_id>", views.video_feed, name='video_feed'),
    path("face_mask_feed", views.face_mask_feed, name='face_mask_feed'),
    # Camera Integration

    path("", views.index, name='index'),
    path("index", views.index, name='index'),
    # path("home", views.home, name="home"),
    path("home", views.location1, name="home"),
    path("records", views.records, name="records"),
    path("download_report", views.download_report, name="download_report"),
    path("notify_user", views.notify_user, name="notify_user"),
    path("doctors-contact", views.doctors_contact, name="doctors-contact"),
    path("forgot-password", views.forgot_password, name="forgot-password"),
    path("edit-account", views.edit_account, name="edit-account"),
    path("location-1", views.location1, name="location-1"),
    path("location-2", views.location2, name="location-2"),
    path("location-3", views.location3, name="location-3"),
    path("location-4", views.location4, name="location-4"),
    path("location-5", views.location5, name="location-5"),
]

from django.db import models


class Place(models.Model):
    location_name = models.CharField(max_length=200)
    ip_url = models.CharField(max_length=200, default='')
    video_name = models.CharField(max_length=200, default='')
    is_alert = models.BooleanField(default=False)

    def __str__(self):
        return self.location_name


class Record(models.Model):
    location = models.ForeignKey(Place, on_delete=models.DO_NOTHING)
    total_people = models.IntegerField(default=0)
    total_violation = models.IntegerField(default=0)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.recorded_at}'


class Doctor(models.Model):
    doc_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.doc_name}'

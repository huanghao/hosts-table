from django.db import models


class HostInfo(models.Model):

    ip = models.CharField(max_length=255, unique=True)
    data = models.TextField()
    updated = models.DateTimeField(auto_now=True)

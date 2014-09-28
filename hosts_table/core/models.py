from django.db import models


class Raw(models.Model):
    ip = models.CharField(max_length=255)
    updated = models.DateTimeField(auto_now=True)
    data = models.TextField()


class Host(models.Model):
    uuid = models.CharField(max_length=255, unique=True)
    sn = models.CharField(max_length=255, db_index=True)
    maintainer = models.CharField(max_length=255, db_index=True)

    hostname = models.CharField(max_length=255, db_index=True)
    ip = models.CharField(max_length=255, db_index=True)

    model = models.CharField(max_length=255)
    cpus = models.CharField(max_length=255)
    memory = models.CharField(max_length=255)
    slots = models.CharField(max_length=255)
    disk = models.CharField(max_length=255)

    updated = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    host = models.ForeignKey(Host)
    updated = models.DateTimeField(auto_now=True)
    comment = models.TextField()

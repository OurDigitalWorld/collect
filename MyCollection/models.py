from django.db import models
from django.contrib.auth.models import User


class Record(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    vita_id = models.CharField(max_length=25)
    url = models.CharField(max_length=150)
    url_thumbnail = models.CharField(max_length=150)
    title = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    user_notes = models.TextField(blank=True, null=True)
    user_tags = models.TextField(blank=True, null=True)
    user_title = models.CharField(max_length=256)


class Group(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    records = models.ManyToManyField(Record, related_name='in_lists', through="Order")
    name = models.CharField(max_length=100, blank=True, null=True)
    public_display = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    group_order = models.FloatField(blank=True, null=True)
    introduction = models.TextField(blank=True, null=True)
    view = models.CharField(max_length=7,blank=True, null=True)


class Order(models.Model):
    number = models.PositiveIntegerField()
    rec = models.ForeignKey(Record, related_name='record_assignment')
    grp = models.ForeignKey(Group)
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

ACCESS_URL_USE_CHOICES = (
    ('full', 'full'),
    ('base', 'base'),
    ('dir', 'dir'),
)

@python_2_unicode_compatible
class AvailabilityOption(models.Model):
    id = models.IntegerField(primary_key=True)
    available = models.BooleanField(help_text="True if the service is available, else false")
    note = models.CharField(max_length=256, blank=True, null=True, help_text="A status message")
    #upSince =
    #downAt =
    #backAt =
    #enabled = models.BooleanField(help_text="Indicate if this status active or not")

    def __str__(self):
        return self.id
class Availability(models.Model):
    enabled = models.ForeignKey(AvailabilityOption, on_delete=models.CASCADE)


@python_2_unicode_compatible
class VOResource_Capability(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=256, blank=True, null=True)  # use choices?
    standardID = models.CharField(max_length=256, blank=True, null=True)  # use choices?
    description = models.CharField(max_length=1024, blank=True, null=True)
    # validationLevel [0..*] -- ignore here

    def __str__(self):
        return self.id


@python_2_unicode_compatible
class VOResource_Interface(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=256, default="vr:WebBrowser")  # use predefined choices here?
    capability = models.ForeignKey(VOResource_Capability, on_delete=models.CASCADE)
    version = models.CharField(max_length=256, blank=True, null=True, default="1.0")
    role = models.CharField(max_length=1024, blank=True, null=True)  # use choices?
    # securityMethod [0..*] -- ignore here

    def __str__(self):
        return self.id


@python_2_unicode_compatible
class VOResource_AccessURL(models.Model):
    id = models.AutoField(primary_key=True)
    interface = models.ForeignKey(VOResource_Interface, on_delete=models.CASCADE)
    url = models.CharField(max_length=1024)
    use = models.CharField(max_length=256, default="full", choices=ACCESS_URL_USE_CHOICES)

    def __str__(self):
        return self.id

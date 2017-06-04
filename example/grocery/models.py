# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from converse.models import AbstractUser, AbstractOrganization


class GroceryUser(AbstractUser):
    pass


class Organization(AbstractOrganization):
    pass


class Order(models.Model):
    item = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    org = models.ForeignKey(to=Organization, related_name='orders')
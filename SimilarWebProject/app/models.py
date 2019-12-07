from django.db import models
from django.core.validators import MinValueValidator


class UniqueSiteTable(models.Model):

    visitor = models.CharField(max_length=50, primary_key=True)
    num_of_unique_sites = models.IntegerField(validators=[
            MinValueValidator(0)
        ])


class SiteMedianTable(models.Model):

    site = models.CharField(max_length=100, primary_key=True)
    median = models.DecimalField(max_digits=30, decimal_places=2)


class NumSessionTable(models.Model):
    site = models.CharField(max_length=100, primary_key=True)
    numSession = models.IntegerField(validators=[
            MinValueValidator(0)
        ])
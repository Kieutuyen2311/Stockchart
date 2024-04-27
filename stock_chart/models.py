from django.db import models

class Stock(models.Model):
    symbol = models.CharField(max_length=255)
    start_date = models.DateField()


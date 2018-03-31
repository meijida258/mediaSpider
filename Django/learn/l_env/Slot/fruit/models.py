from django.db import models
from django.contrib import admin

# Create your models here.
class SlotRecord(models.Model):
    reward1_prob = models.FloatField()
    reward2_prob = models.FloatField()
    reward3_prob = models.FloatField()
    no_reward_prob = models.FloatField()
    total_reward = models.IntegerField()
    user_money = models.IntegerField()
    current_chips = models.IntegerField()
    current_result = models.CharField(max_length=10)
    current_user_reward = models.IntegerField()


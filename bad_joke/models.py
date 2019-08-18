from django.db import models
import uuid
from numpy.random import randint

class ChatUser(models.Model):
    chat_id = models.IntegerField(default=0)
    first_name = models.CharField(max_length=140, blank=True, null=True)
    last_name = models.CharField(max_length=140, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_answer = models.BooleanField(default=False)
    is_in_game = models.BooleanField(default=False)
    is_winner = models.BooleanField(default=False)
    answer = models.CharField(max_length=500, blank=True, null=True)
    score = models.IntegerField(default=0)
    number_of_vote = models.IntegerField(default=0)
    is_vote = models.BooleanField(default=False)

    game_score = models.IntegerField(default=0)
    is_admin = models.BooleanField(default=False)

    # is_answer = models.UUIDField(default=uuid.uuid4, blank=False, null=False, unique=True)

    def __str__(self):
        return self.first_name

class JokeText(models.Model):
    joke_text = models.CharField(max_length=500, blank=True, null=True)
# Create your models here.

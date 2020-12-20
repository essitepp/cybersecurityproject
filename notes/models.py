from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
  note_title = models.CharField(max_length=20)
  note_text = models.TextField()
  owner = models.ForeignKey(User, on_delete=models.CASCADE)
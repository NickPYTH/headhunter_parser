from django.db import models

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    question_mark = models.IntegerField()
    question_mark = models.TextField()
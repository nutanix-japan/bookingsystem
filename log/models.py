from django.db import models
from django.utils import timezone
import datetime

def writelog(message):
  Log(message=message).save()

# Create your models here.
class Log(models.Model):
  timestamp = models.DateTimeField(default=timezone.now)
  message = models.CharField(max_length=500)

  def __str__(self):
    text = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    text += ' {}'.format(self.message)
    return text

  class Meta:
    ordering = ['-timestamp']
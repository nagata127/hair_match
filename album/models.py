from django.db import models

class Document(models.Model):
    photo = models.ImageField(upload_to = 'image/')

def __str__(self):
    return self.content

# Create your models here.

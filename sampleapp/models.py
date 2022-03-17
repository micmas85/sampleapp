from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
       

class WorkOrder(models.Model):
    title = models.CharField(max_length=64, verbose_name="Title")
    description = models.TextField(verbose_name="Description", blank=True, null=True)
    statusChoices = [("NEW", "NEW"), ("IN_PROGRESS", "IN PROGRESS"), ("ON_HOLD", "ON HOLD"), ("COMPLETED", "COMPLETED"), ("CANCELLED", "CANCELLED")]
    status = models.CharField(max_length=32, verbose_name="Status", choices=statusChoices, default="NEW")
    created_by = models.ForeignKey(User, models.DO_NOTHING, related_name="created_by", verbose_name="Created by", blank=True, null=True, editable=False)
    created_at = models.DateTimeField(editable=False, verbose_name="Created at", auto_now_add=True)
    updated_at = models.DateTimeField(editable=False, verbose_name="Updated at", default=datetime.now())
    assigned_to = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="assigned_to", verbose_name="Assigned to", null=True, blank=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(WorkOrder, self).save(*args, **kwargs)  
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Work order'
        verbose_name_plural = 'Work orders'

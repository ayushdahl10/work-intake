import shortuuid
from django.db import models


class BaseModel(models.Model):
    uid = models.CharField(max_length=255,editable=False,unique=True,null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def save(self,*args,**kwars):
        if not self.uid:
            self.uid=shortuuid.ShortUUID().random(length=22)
        super().save(*args, **kwars)

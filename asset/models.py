from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from account.models import Group

class Asset(models.Model):
  name = models.CharField(max_length=100, unique=True)
  modelNumber = models.CharField(max_length=100, blank=True, verbose_name="Model Number")
  serialNumber = models.CharField(max_length=100, blank=True, verbose_name="Serial Number")
  installationDate = models.DateField(null=True, blank=True, verbose_name="Installation Date")
  expirationDate = models.DateField(null=True, blank=True, verbose_name="Expiration Date")
  ownerGroup = models.ForeignKey(Group, on_delete=models.PROTECT, null=True)
  is_active = models.BooleanField(default=True, verbose_name="Active")
  note = models.TextField(blank=True, verbose_name="Note")

  def __str__(self):
    return self.name

  def get_absolute_url(self):
    return reverse('asset_list')

  def clean(self):
    if self.installationDate is not None:
      if self.expirationDate is None:
        raise ValidationError('Create/Update failed. Needs "Expiration Date" if having "Installation Date".')

    if self.expirationDate is not None:
      if self.installationDate is None:
        raise ValidationError('Create/Update failed. Needs "Installation Date" if having "Expiration Date".')

    if self.installationDate is None:
      return

    if self.installationDate > self.expirationDate:
      raise ValidationError('Create/Update failed. "Expiration Date" must be greater than "Installation Date".')

  class Meta:
    ordering = ['name']
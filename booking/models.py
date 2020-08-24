from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse, reverse_lazy

from asset.models import Asset

import datetime

class Booking(models.Model):
  fromDate = models.DateField(verbose_name="Start Date")
  toDate = models.DateField(verbose_name="End Date")
  shippingDate = models.DateField(null=True, blank=True, verbose_name="Shipping Date")
  returnDate = models.DateField(null=True, blank=True, verbose_name="Return Date")

  asset = models.ForeignKey('asset.Asset', on_delete=models.CASCADE)
  ownerUser = models.ForeignKey('account.User', on_delete=models.CASCADE, verbose_name="Owner User")
  ownerGroup = models.ForeignKey('account.Group', on_delete=models.CASCADE, verbose_name="Owner Group")
  purpose = models.CharField(max_length=100, blank=True, verbose_name="Purpose")
  note = models.TextField(blank=True, verbose_name="Note")

  def get_absolute_url(self):
    return reverse('home')

  class Meta:
    ordering = ['asset', 'fromDate']

  def __str__(self):
    return '{}({},{}) {} -> {}'.format(self.asset, self.ownerUser, 
      self.ownerGroup, self.fromDate, self.toDate)

  # Create and Update Validation
  def clean(self):
    self._check_asset_active()
    self._check_dates()
    self._check_asset_expiration()
    self._check_booking_conflict()

  def _check_asset_active(self):
    is_active = self.asset.is_active
    if not is_active:
      raise ValidationError('Create/Update failed. The asset is inactive.')

  def _check_dates(self):
    if self.shippingDate is not None:
      if self.returnDate is None:
        raise ValidationError('Create/Update failed. Needs "Return Date" if having "Shipping Date".')

      if self.fromDate > self.shippingDate:
        raise ValidationError('Create/Update failed. "Shipping Date" must be greater than "From Date".')

      if self.shippingDate > self.returnDate:
        raise ValidationError('Create/Update failed. "Return Date" must be greater than "Shipping Date".')
    else:
      if self.returnDate is not None:
        raise ValidationError('Create/Update failed. Needs "Shipping Date" if having "Return Date".')

    # Check ToDate
    if self.returnDate is None:
      if self.fromDate > self.toDate:
        raise ValidationError('Create/Update failed. "To Date" must be greater than "From Date".')
    else:
      if self.returnDate > self.toDate:
        raise ValidationError('Create/Update failed. "To Date" must be greater than "Return Date".')

  def _check_asset_expiration(self):
    expDate = self.asset.expirationDate
    if expDate is None:
      return

    if self.toDate < expDate:
      # ok
      pass
    else:
      raise ValidationError('Create/Update failed. "To Date" must be less than asset\'s "expiration Date".')

  def _check_booking_conflict(self):
    asset_pk = self.asset.pk
    f = self.fromDate
    t = self.toDate
    conflict_bookings = Booking.objects.filter(
    asset=asset_pk).filter(
    toDate__gte=datetime.date(f.year, f.month, f.day)).filter(
    fromDate__lte=datetime.date(t.year, t.month, t.day))
 
    if self.pk is not None:
      # not create but update
      if(len(conflict_bookings) == 1):
        if conflict_bookings[0].pk == self.pk:
          # the only conflict booking is oneself. OK
          return

    if(len(conflict_bookings) != 0):
      text = 'Create/Update failed. Having conflict with booking ['
      for booking in conflict_bookings:
        if booking.pk == self.pk:
          # booking is oneself.
          continue
        text += '"{}", '.format(booking)
      text += ']'
      raise ValidationError(text)
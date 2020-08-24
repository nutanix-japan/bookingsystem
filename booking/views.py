# View
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic import CreateView, UpdateView, DeleteView

# View helper
from django.http import HttpResponse
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages

# Model
from booking.models import Booking

# util
from log.models import writelog
import datetime

class IndexView(TemplateView):
  template_name = 'booking/index.html'

class BookingListView(ListView):
  model = Booking
  template_name = 'booking/list.html'

  def get_queryset(self):
    today = datetime.date.today()
    object_list = self.model.objects.filter(toDate__gte = today)
    return object_list

class BookingDetailView(DetailView):
  model = Booking
  template_name = 'booking/detail.html'

class BookingCreateView(CreateView):
  model = Booking
  template_name = 'booking/create.html'
  fields = '__all__'
  success_url = reverse_lazy('home')

  def form_valid(self, form):
    ins = form.instance
    text = 'user {} creates booking. asset {} from {} to {} for "{}"'.format(
      self.request.user,
      ins.asset.name, ins.fromDate, ins.toDate, ins.purpose)
    writelog(text)
    return super(BookingCreateView, self).form_valid(form)

  def form_invalid(self, form):
    error = form.errors['__all__'][0]
    messages.error(self.request, error)
    print(error)
    return super(BookingCreateView, self).form_invalid(form)

  def get_initial(self):
    initial = {}

    # Set user if logined (shoule be controlled to login only by urls.py)
    if self.request.user.is_authenticated:
      initial['ownerUser'] = self.request.user

      group = self.request.user.group
      if group is not None:
        initial['ownerGroup'] = group

    return initial

class BookingUpdateView(UpdateView):
  model = Booking
  template_name = 'booking/update.html'
  fields = '__all__'

  def form_valid(self, form):
    ins = form.instance
    text = 'user {} updates booking. asset {} from {} to {} for "{}"'.format(
      self.request.user,
      ins.asset.name, ins.fromDate, ins.toDate, ins.purpose)
    writelog(text)
    return super(BookingUpdateView, self).form_valid(form)

  def form_invalid(self, form):
    error = form.errors['__all__'][0]
    messages.error(self.request, error)
    print(error)
    return super(BookingUpdateView, self).form_invalid(form)

def releaseBooking(request, pk):
  query_set = Booking.objects.filter(pk=pk)
  if len(query_set) != 1:
    return HttpResponseBadRequest()

  booking = query_set[0] 
  today = datetime.date.today()

  # Delete
  if booking.fromDate > today:
    text = 'user {} deletes booking. asset {} from {} to {} for "{}"'.format(
      request.user, booking.asset.name, booking.fromDate, booking.toDate, booking.purpose)
    booking.delete()
    writelog(text)

  # Set toDate to today
  elif booking.toDate > today:
    if booking.shippingDate is not None:
      if booking.shippingDate > today:
        booking.shippingDate = today
    if booking.returnDate is not None:
      if booking.returnDate > today:
        booking.returnDate = today
    booking.toDate = today
    text = 'user {} releases booking. asset {} from {} to {} for "{}"'.format(
      request.user, booking.asset.name, booking.fromDate, booking.toDate, booking.purpose)   
    booking.save()
    writelog(text)

  return HttpResponseRedirect(reverse_lazy('home'))

def test(request):
  #writelog('this is a test.')
  print(request.user)
  print(type(request.user))
  return HttpResponse('ok') 

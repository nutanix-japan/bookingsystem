from django.shortcuts import render
from .models import Asset
from django.urls import reverse_lazy

from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib import messages

from django.core.serializers import serialize
from log.models import writelog
import json

class AssetListView(ListView):
  model = Asset
  template_name = 'asset/list.html'

class AssetDetailView(DetailView):
  model = Asset
  template_name = 'asset/detail.html'

class AssetCreateView(CreateView):
  model = Asset
  template_name = 'asset/create.html'
  fields = ('name', 'modelNumber', 'serialNumber', 'installationDate', 'expirationDate', 'is_active', 'note')

  def form_valid(self, form):
    ins = form.instance
    text = 'user {} creates asset {}. modelNumber:{}, serialNumber:{}'.format(
      self.request.user, ins.name, ins.modelNumber, ins.serialNumber)
    writelog(text)
    return super(AssetCreateView, self).form_valid(form)

  def form_invalid(self, form):
    '''
    error = form.errors['__all__'][0]
    messages.error(self.request, error)
    '''
    print(form.errors)
    return super(AssetCreateView, self).form_invalid(form)

class AssetUpdateView(UpdateView):
  model = Asset
  template_name = 'asset/update.html'
  fields = ('name', 'modelNumber', 'serialNumber', 'installationDate', 'expirationDate', 'is_active', 'note')

  def form_valid(self, form):
    ins = form.instance
    text = 'user {} updates asset {}. modelNumber:{}, serialNumber:{}'.format(
      self.request.user, ins.name, ins.modelNumber, ins.serialNumber)
    writelog(text)
    return super(AssetUpdateView, self).form_valid(form)

  def form_invalid(self, form):
    error = form.errors['__all__'][0]
    messages.error(self.request, error)
    return super(AssetUpdateView, self).form_invalid(form)

class AssetDeleteView(DeleteView):
  model = Asset
  template_name = 'asset/delete.html'
  success_url = reverse_lazy('asset_list')

  def delete(self, request, *args, **kwargs):
    asset = Asset.objects.get(pk=self.kwargs['pk'])
    text = 'user {} deletes asset {}. modelNumber:{}, serialNumber:{}'.format(
      self.request.user, asset.name, asset.modelNumber, asset.serialNumber)
    writelog(text)
    return super(AssetDeleteView, self).delete(request, *args, **kwargs)
from django.shortcuts import render
from django.views.generic import TemplateView

class StatView(TemplateView):
  template_name = 'statapp/stat.html'

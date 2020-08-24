from django.shortcuts import render
from django.views.generic import TemplateView

class HelpView(TemplateView):
  template_name = 'helpapp/help.html'

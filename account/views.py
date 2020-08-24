from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.views import PasswordChangeView as AuthPasswordChangeView
from django.contrib.auth.views import PasswordChangeDoneView as AuthPasswordChangeDoneView
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login

from .models import User, Group, UserCreationForm, UserPasswordResetForm
from django.urls import reverse, reverse_lazy
from log.models import writelog

from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth.views import LogoutView as AuthLogoutView

from django.http import HttpResponseBadRequest, HttpResponseRedirect

from django.db import models

########
## GROUP
########

class GroupListView(ListView):
  model = Group
  template_name = 'account/group_list.html'

class GroupDetailView(DetailView):
  model = Group
  template_name = 'account/group_detail.html'

class GroupCreateView(CreateView):
  model = Group
  template_name = 'account/group_create.html'
  fields = '__all__'

class GroupUpdateView(UpdateView):
  model = Group
  template_name = 'account/group_update.html'
  fields = '__all__'

class GroupDeleteView(DeleteView):
  model = Group
  template_name = 'account/group_delete.html'

  def delete(self, request, *args, **kwargs):
    try:
      self.object = self.get_object()
      self.object.delete()
      success_url = reverse_lazy('account_group_list')
      return HttpResponseRedirect(success_url)

    except models.ProtectedError:
      group = Group.objects.get(pk=self.kwargs['pk'])
      messages.error(request, 'Deleting group "{}" failed. Group might have users. Please delete/move users who belong to this group.'.format(group.name))
      error_url = reverse_lazy('account_group_list')
      return HttpResponseRedirect(error_url) 


#######
## USER
#######

## by staff

class UserListView(ListView):
  model = User
  template_name = 'account/user_list.html'

class UserDetailView(DetailView):
  model = User
  template_name = 'account/user_detail.html'

class UserCreateView(CreateView):
  model = User
  form_class = UserCreationForm
  template_name = 'account/user_create.html'
  #fields = '__all__'

  def form_valid(self, form):
    print('form_valid')
    '''
    ins = form.instance
    text = 'user {} creates asset {}. modelNumber:{}, serialNumber:{}'.format(
      self.request.user, ins.name, ins.modelNumber, ins.serialNumber)
    writelog(text)
    '''
    return super(UserCreateView, self).form_valid(form)

  def form_invalid(self, form):
    print('form_invalid')
    print(form.errors)
    '''
    error = form.errors['__all__'][0]
    messages.error(self.request, error)
    '''

    return super(UserCreateView, self).form_invalid(form)

class UserStaffUpdateView(UpdateView):
  model = User
  template_name = 'account/user_staff_update.html'
  fields = ('username', 'group', 'email', 'is_active', 'is_staff', 'note')

  def form_valid(self, form):
    print('form_valid')
    '''
    ins = form.instance
    text = 'user {} creates asset {}. modelNumber:{}, serialNumber:{}'.format(
      self.request.user, ins.name, ins.modelNumber, ins.serialNumber)
    writelog(text)
    '''
    return super(UserStaffUpdateView, self).form_valid(form)

  def form_invalid(self, form):
    print('form_invalid')
    print(form.errors)
    '''
    error = form.errors['__all__'][0]
    messages.error(self.request, error)
    '''

    return super(UserStaffUpdateView, self).form_invalid(form)

class UserDeleteView(DeleteView):
  model = User
  template_name = 'account/user_delete.html'
  success_url = reverse_lazy('account_user_list')


class UserPasswordResetView(FormView):
  model = User
  template_name = 'account/user_password_reset.html'
  success_url = reverse_lazy('account_user_list')
  form_class = UserPasswordResetForm

  def form_valid(self, form):
    # password1 and password2 are same.
    password = form.cleaned_data['password1']
    user = User.objects.get(pk=self.kwargs['pk'])
    print(user.is_superuser)
    if not user.is_superuser:
      user.set_password(password)
      user.save()
    return super(UserPasswordResetView, self).form_valid(form)

  def form_invalid(self, form):
    print('form_invalid')
    print(form.errors)
    error = form.errors['__all__'][0]
    messages.error(self.request, error)
    return super(UserPasswordResetView, self).form_invalid(form)      

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    user = User.objects.get(pk=self.kwargs['pk'])
    context['username'] = user.username
    context['groupname'] = user.group
    return context


## by oneself

class UserSelfUpdateView(UpdateView):
  model = User
  fields = ('first_name', 'last_name', 'email')
  template_name = 'account/user_self_update.html'
  success_url = reverse_lazy('account_user_self_update')

  def get_object(self):
    return self.request.user

  def form_valid(self, form):
    writelog('user {} updates his/her profile'.format(self.request.user))
    return super(UserSelfUpdateView, self).form_valid(form)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    if self.request.user.is_authenticated:
      group = self.request.user.group
      if group is not None:
        context['group_name'] = group
      else:
        context['group_name'] = ''
    return context

class PasswordChangeView(AuthPasswordChangeView):
  template_name = 'account/password_change.html'
  success_url = reverse_lazy('account_password_change_done')

class PasswordChangeDoneView(AuthPasswordChangeDoneView):
  template_name = 'account/password_change_done.html'

  def dispatch(self, request, *args, **kwargs):
    writelog('user {} updates his/her password'.format(self.request.user))
    return super(PasswordChangeDoneView, self).dispatch(request, *args, **kwargs)


#######
## LOGIN/LOGOUT
#######

class LoginView(AuthLoginView):
  template_name = 'account/password_login.html'

  def form_valid(self, form):
    writelog('user {} login'.format(form.get_user()))
    return super(LoginView, self).form_valid(form)

  def form_invalid(self, form):
    username = form.data['username']
    query = User.objects.filter(username=username)
    if len(query) == 0:
      text = 'Login failed. User "{}" does not exist.'.format(username)
      writelog(text)
      messages.error(self.request, text)
    else:
      user = query[0]
      if user.is_active:
        text = 'Login failed with user "{}". Password might be wrong.'.format(username)
        writelog(text)
        messages.error(self.request, text)
      else:
        text = 'User "{}" is inactive. Please contact admin to make active.'.format(username)
        writelog(text)
        messages.error(self.request, text)

    return super(LoginView, self).form_invalid(form)


class LogoutView(AuthLogoutView):
  def dispatch(self, request, *args, **kwargs):
    writelog('user {} logout'.format(self.request.user))
    return super(LogoutView, self).dispatch(request, *args, **kwargs)


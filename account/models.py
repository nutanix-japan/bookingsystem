from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

#from .form import UserCreationForm

class Group(models.Model):
  name = models.CharField(max_length=150)
  backgroundColor = models.CharField(max_length=150)
  textColor = models.CharField(max_length=150)
  note = models.TextField(blank=True, verbose_name="Note")

  class Meta:
    ordering = ['name']

  def get_absolute_url(self):
    return reverse('account_group_list')

  def __str__(self):
    return self.name

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=150, unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    group = models.ForeignKey(Group, on_delete=models.PROTECT, null=True)
    note = models.TextField(blank=True, verbose_name="Note")

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        ordering = ['username']
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('account_user_list')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    # 既存メソッドの変更
    def get_full_name(self):
        return self.first_name

    def get_short_name(self):
        return self.first_name


class UserManager(BaseUserManager):
    """ユーザーマネージャー."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """メールアドレスでの登録を必須にする"""
        '''
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        '''

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """is_staff(管理サイトにログインできるか)と、is_superuer(全ての権限)をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """スーパーユーザーは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user


####
# FORM
####

from django.contrib.auth.forms import UserCreationForm as AuthUserCreationForm
from django import forms

class UserCreationForm(AuthUserCreationForm):
 
  class Meta(AuthUserCreationForm.Meta):
    model = User
    fields = ('username', 'group', 'password1', 'password2', 'email', 'is_active', 'is_staff', 'note')

class UserPasswordResetForm(forms.Form):
  password1 = forms.CharField(min_length=8, widget=forms.PasswordInput(), label='Password')
  password2 = forms.CharField(min_length=8, widget=forms.PasswordInput(), label='Password confirmation')

  def clean(self):
    cleaned_data = super().clean()
    print('form clean')
    p1 = cleaned_data['password1']
    p2 = cleaned_data['password2']
    print(p1)
    print(p2)

    if p1 != p2:
        print('validationError')
        raise forms.ValidationError('Passwords are different.')

    return cleaned_data  


    #AuthUserCreationForm.Meta.fields + ('note', 'group', 'password')

'''
class GroupColor(models.Model):
  group = models.ForeignKey('auth.Group', on_delete=models.CASCADE)
  color = models.CharField(max_length=100)
  rgb = models.CharField(max_length=100)
  textColor = models.CharField(max_length=100)
  textRgb = models.CharField(max_length=100)

  def __str__(self):
    return '{}: {}({}) {}({})'.format(self.group, self.color, self.rgb,
      self.textColor, self.textRgb)
'''
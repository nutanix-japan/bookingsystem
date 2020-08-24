from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required

import django.contrib.auth.views
import account.views
import asset.views
import booking.views
import booking.api
import statapp.views
import log.views
import helpapp.views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home(Booking)
    path('', booking.views.IndexView.as_view(), name='home'),

    # Account 
    path('account/login', account.views.LoginView.as_view(), name='account_login'),
    path('account/logout', login_required(account.views.LogoutView.as_view()), name='account_logout'),

    # Account user management by oneself
    path('account/password_change', login_required(account.views.PasswordChangeView.as_view()), name='account_password_change'),
    path('account/password_change_done', account.views.PasswordChangeDoneView.as_view(), name='account_password_change_done'),
    path('account/user_self_update', login_required(account.views.UserSelfUpdateView.as_view()), name='account_user_self_update'),

    # Account group management
    path('account/group/', login_required(account.views.GroupListView.as_view()), name='account_group_list'),
    path('account/group/create', login_required(account.views.GroupCreateView.as_view()), name='account_group_create'),
    path('account/group/<int:pk>/detail', account.views.GroupDetailView.as_view(), name='account_group_detail'),
    path('account/group/<int:pk>/update', login_required(account.views.GroupUpdateView.as_view()), name='account_group_update'),
    path('account/group/<int:pk>/delete', login_required(account.views.GroupDeleteView.as_view()), name='account_group_delete'),

    # Account user management by staff-user
    path('account/user/', login_required(account.views.UserListView.as_view()), name='account_user_list'),
    path('account/user/create', login_required(account.views.UserCreateView.as_view()), name='account_user_create'),
    path('account/user/<int:pk>/detail', account.views.UserDetailView.as_view(), name='account_user_detail'),
    path('account/user/<int:pk>/update', login_required(account.views.UserStaffUpdateView.as_view()), name='account_user_staff_update'),
    path('account/user/<int:pk>/delete', login_required(account.views.UserDeleteView.as_view()), name='account_user_delete'),    
    path('account/user/<int:pk>/password_reset', login_required(account.views.UserPasswordResetView.as_view()), name='account_user_password_reset'),  

    # Booking
    path('booking/', booking.views.BookingListView.as_view(), name='booking_list'),
    path('booking/create', login_required(booking.views.BookingCreateView.as_view()), name='booking_create'),
    path('booking/<int:pk>/detail', booking.views.BookingDetailView.as_view(), name='booking_detail'),
    path('booking/<int:pk>/update', login_required(booking.views.BookingUpdateView.as_view()), name='booking_update'),
    path('booking/<int:pk>/release', login_required(booking.views.releaseBooking), name='booking_release'),

    # Booking API
    path('api/v1/booking/', booking.api.BookingApi.get_assets, name='api_bookinglist'),
    path('api/v1/booking/<int:asset_pk>', booking.api.BookingApi.get_asset, name='api_booking_asset'),

    # Asset
    path('asset/', asset.views.AssetListView.as_view(), name='asset_list'),
    path('asset/create', login_required(asset.views.AssetCreateView.as_view()), name='asset_create'),
    path('asset/<int:pk>/detail', asset.views.AssetDetailView.as_view(), name='asset_detail'),
    path('asset/<int:pk>/update', login_required(asset.views.AssetUpdateView.as_view()), name='asset_update'),
    path('asset/<int:pk>/delete', login_required(asset.views.AssetDeleteView.as_view()), name='asset_delete'),

    # Stat
    path('stats/', statapp.views.StatView.as_view(), name='stat'),

    # Log
    path('log/', log.views.LogListView.as_view(), name='log'),

    # Help
    path('help/', helpapp.views.HelpView.as_view(), name='help'),

    # Test
    path('test', account.views.UserPasswordResetView.as_view()),
]

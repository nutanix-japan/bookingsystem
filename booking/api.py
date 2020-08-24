from django.http import JsonResponse, HttpResponse
from django.core.serializers import serialize

# Model
from booking.models import Booking
from asset.models import Asset
#from account.models import GroupColor
#from django.contrib.auth.models import User, Group
from account.models import User, Group

import json
import datetime

class BookingApi:
  DEFAULT_GROUP_COLOR = 'gray'
  DEFAULT_GROUP_RGB = 'rgb(127,127,127)'
  DEFAULT_GROUP_TEXT_COLOR = 'gray'
  DEFAULT_GROUP_TEXT_RGB = 'rgb(255,255,255)'

  @classmethod
  def get_assets(cls, request):
    group_map = cls._get_group_map()
    user_map = cls._get_user_map()
    asset_map = cls._get_asset_map()

    # grouping asset bookings by asset.
    asset_booking_map = cls._get_asset_booking_map(group_map, user_map, asset_map)

    # sort by assetName(row) and fromDate(column)
    asset_booking_table = cls._get_asset_booking_table(asset_map, asset_booking_map)

    response_body = json.dumps(asset_booking_table, indent=2)
    return HttpResponse(response_body, content_type='application/json')

  @classmethod
  def get_asset(cls, request, asset_pk):
    group_map = cls._get_group_map()
    user_map = cls._get_user_map()

    # only the asset
    asset_map = cls._get_asset_map(asset_pk)
    asset_booking_map = cls._get_asset_booking_map(group_map, user_map, asset_map, asset_pk)
    
    asset_booking_table = cls._get_asset_booking_table(asset_map, asset_booking_map)
    response_body = json.dumps(asset_booking_table, indent=2)
    return HttpResponse(response_body, content_type='application/json')


  @classmethod
  def _get_group_map(cls):
    group_list = json.loads(serialize('json', Group.objects.all()))
    group_map = {}
    for group in group_list:
      d = {}
      d['name'] = group['fields']['name']
      d['backgroundColor'] = group['fields']['backgroundColor']
      d['textColor'] = group['fields']['textColor']
      group_map[group['pk']] = d
    return group_map
          
  @classmethod
  def _get_user_map(cls):
    user_list = json.loads(serialize('json', User.objects.all()))
    user_map = {}
    for user in user_list:
      d = {}
      d['name'] = user['fields']['username']
      user_map[user['pk']] = d
    return user_map

  @classmethod
  def _get_asset_map(cls, pk=None):
    if pk is None:
      asset_list = json.loads(serialize('json', Asset.objects.all()))
    else:
      asset_list = json.loads(serialize('json', Asset.objects.filter(pk=pk)))

    asset_map = {}
    for asset in asset_list:
      asset_map[asset['pk']] = asset['fields']

    return asset_map

  @classmethod
  def _get_asset_booking_map(cls, group_map, user_map, asset_map, asset_pk=None):
    asset_booking_map = {}
    for asset_id, asset_dict in asset_map.items():
      asset_booking_map[asset_id] = {'assetName':asset_dict['name'], 'bookings':[]}

    if asset_pk is None:
      booking_list = json.loads(serialize('json', Booking.objects.all()))
    else:
      assets = Asset.objects.filter(pk=asset_pk)
      if len(assets) == 0:
        return asset_booking_map
      asset = assets[0]
      booking_list = json.loads(serialize('json', Booking.objects.filter(asset=asset)))

    for booking in booking_list:
      asset_id = booking['fields']['asset']
      if asset_id not in asset_map:
        continue

      d = {}
      d['bookingId'] = booking['pk']
      for (key, value) in booking['fields'].items():
        if key == 'ownerUser':
          if value not in user_map:
            #should not be happen (bug)
            continue
          d['ownerUserId'] = value
          d['ownerUserName'] = user_map[value]['name']
        elif key == 'ownerGroup':
          if value not in group_map:
            #should not happen
            continue
          d['ownerGroupId'] = value
          d['ownerGroupName'] = group_map[value]['name']
          d['backgroundColor'] = group_map[value]['backgroundColor']
          d['textColor'] = group_map[value]['textColor']

          '''
          # set color by group
          if value not in groupcolor_map:
            #should not be happen (no DB entry)
            d['backgroundColor'] = cls.DEFAULT_GROUP_COLOR
            #d['rgb'] = cls.DEFAULT_GROUP_RGB
            d['textColor'] = cls.DEFAULT_GROUP_TEXT_COLOR
            #d['textRgb'] = cls.DEFAULT_GROUP_TEXT_RGB
          else:
            d['backgroundColor'] = groupcolor_map[value]['color']
            #d['rgb'] = groupcolor_map[value]['rgb']
            d['textColor'] = groupcolor_map[value]['textColor']
            #d['textRgb'] = groupcolor_map[value]['textRgb'] 
          '''
        elif key == 'asset':
          continue
        else:
          d[key] = value

      asset_booking_map[asset_id]['bookings'].append(d)

    return asset_booking_map

  @classmethod
  def _get_asset_booking_table(cls, asset_map, asset_booking_map):
    asset_booking_table = []
    for key, value in sorted(asset_booking_map.items(), key=lambda x:x[1]['assetName']):
      d = {}
      d['assetId'] = key
      d['assetName'] = value['assetName']
      d['assetModelNumber'] = asset_map[key]['modelNumber']
      d['assetSerialNumber'] = asset_map[key]['serialNumber']
      d['assetInstallationDate'] = asset_map[key]['installationDate']
      d['assetExpirationDate'] = asset_map[key]['expirationDate']
      d['active'] = asset_map[key]['is_active']
      d['assetNote'] = asset_map[key]['note']
      
      sorted_booking = sorted(value['bookings'], key=lambda x:x['fromDate'])
      d['bookings'] = sorted_booking
      asset_booking_table.append(d) 

    return asset_booking_table
import datetime
from math import floor

from django.shortcuts import render_to_response
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from blog import models
from blog.runkeeper import RunkeeperInterface
from blog.soundcloud_interface import SoundcloudInterface


runkeeper_format = '%a, %d %b %Y %H:%M:%S'
soundcloud_format = '%Y/%m/%d %H:%M:%S'


def short_date(dt):
    now = timezone.now()
    timedelta = now - timezone.make_aware(dt, timezone.get_default_timezone())
    days = timedelta.days
    if days:
        if days < 30:
            formatted = '%dd' % days
        elif days < 365:
            formatted = '%dm' % (days / 30)
        else:
            formatted = '%dy' % (days / 365)
    else:
        seconds = timedelta.seconds
        if seconds < 60:
            formatted = '%ds' % seconds
        elif seconds < 60 * 60:
            formatted = '%dm' % floor(seconds / 60)
        else:
            formatted = '%dh' % floor(seconds / 60 / 60)
    return formatted


def _parse_runkeeper_date_string(date_string):
    dt = datetime.datetime.strptime(date_string, runkeeper_format)
    return dt

def _parse_soundcloud_date_string(date_string):
    dt = datetime.datetime.strptime(date_string, soundcloud_format)
    return dt


def index(request):
    raw_runkeeper = RunkeeperInterface().fitness_activity()
    latest_runkeeper = raw_runkeeper[0]
    # u'Sat, 24 May 2014 22:10:31'
    date_string = latest_runkeeper['start_time']
    dt = _parse_runkeeper_date_string(date_string)
    distance = 0
    seconds = 0
    for record in raw_runkeeper:
        parsed_date = timezone.make_aware(_parse_runkeeper_date_string(record['start_time']), timezone.get_default_timezone())
        last_month = timezone.now() + relativedelta(months=-1)
        if parsed_date < last_month:
            break
        else:
            distance += record['total_distance']
            seconds += record['duration']
    latest_runkeeper = {
        'distance': (round(latest_runkeeper['total_distance']) / 1000),
        'time': round(latest_runkeeper['duration'] / 60, 2),
        'date': short_date(dt),

    }
    context = {
        'posts': models.Post.objects.all(),
        'latest_runkeeper': latest_runkeeper,
        'runkeeper_total_distance': round(distance / 1000),
        'runkeeper_total_duration': round(seconds / 60, 2),
    }
    track = SoundcloudInterface().latest_track_share()
    parsed_track = {}
    if track:
        origin = track['origin']
        if origin:
            title = origin.get('title')
            url = origin.get('permalink_url')
            created_at = origin.get('created_at')
            if title and url and created_at:
                dt = short_date(_parse_soundcloud_date_string(created_at.split('+')[0].strip()))
                parsed_track['date'] = dt
                parsed_track['title'] = title
                parsed_track['url'] = url
                artwork_url = origin.get('artwork_url')
                if artwork_url:
                    parsed_track['artwork_url'] = artwork_url
                user = origin.get('user')
                if user:
                    username = user.get('username')
                    if username:
                        parsed_track['username'] = username
    if parsed_track:
        context['latest_soundcloud'] = parsed_track
    return render_to_response('blog/index.html', context)


def smooth(request):
    return render_to_response('smooth.html')


def admin(request):
    return render_to_response('admin.html')
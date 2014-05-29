import datetime
from math import floor
from django.http import Http404

from django.shortcuts import render_to_response
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.views.generic import View
from dropbox.rest import ErrorResponse
from django.core.context_processors import csrf

from blog import models
from blog.dropbox_interface import DropboxInterface
from blog.models import Post
from blog.runkeeper import RunkeeperInterface
from blog.soundcloud_interface import SoundcloudInterface


runkeeper_format = '%a, %d %b %Y %H:%M:%S'
soundcloud_format = '%Y/%m/%d %H:%M:%S'


def short_date(dt):
    now = timezone.now()
    if not dt.tzinfo:
        dt = timezone.make_aware(dt, timezone.get_default_timezone())
    timedelta = now - dt
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
        'posts': models.Post.objects.all().order_by('-published_date')[0:5],
        'latest_runkeeper': latest_runkeeper,
        'runkeeper_total_distance': round(distance / 1000),
        'runkeeper_total_duration': round(seconds / 60, 2),
        'num_posts': models.Post.objects.count()
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


class ExternalError(Exception):
    def __init__(self, message, *args, **kwargs):
        super(ExternalError, self).__init__(*args, **kwargs)
        self.message = message


class AdminView(View):
    def render(self, request, **kwargs):
        files = DropboxInterface().resolve()
        context = {
            'files': files,
        }
        context.update(csrf(request))
        context.update(kwargs)
        return render_to_response('admin.html', context)

    def get(self, request):
        return self.render(request)

    def _unpublish(self, post):
        post.revision = None
        post.save()

    def _read_file_path_from_dropbox(self, file_path):
        try:
            data, metadata = DropboxInterface().read(file_path)
            return data, metadata
        except ErrorResponse as e:
            raise ExternalError('%d: %s' % (e.status, e.error_msg))

    def _rename_file_on_dropbox(self, to_path, from_path):
        try:
            DropboxInterface().mv(from_path=from_path, to_path=to_path)
        except ErrorResponse as  e:
            raise ExternalError('%d: %s' % (e.status, e.error_msg))

    def _find_on_dropbox(self, post):
        p = post.dropbox_file_pattern
        files = DropboxInterface().find(p)
        n = len(files)
        if n > 1:
            raise ExternalError('Post %d has more than one file match: %s. Need to delete one.' % (post.pk, files))
        elif not n:
            raise ExternalError('Could not find any files matching %s' % p)
        else:
            return files[0]


    def _publish(self, post):
        file_path = self._find_on_dropbox(post)
        data, metadata = self._read_file_path_from_dropbox(file_path)
        post.markdown = data
        post.revision = metadata['revision']
        post.save()

    def _process(self, file_path):
        data, metadata = self._read_file_path_from_dropbox(file_path)
        post = Post.objects.create(markdown=data)
        splt = file_path.split('.')
        to_path = '.'.join(splt[:-1] + [str(post.pk), splt[-1]])
        self._rename_file_on_dropbox(from_path=file_path, to_path=to_path)

    def post(self, request):
        for k, v in request.POST.iteritems():
            if k.startswith('cmd'):
                pk_or_file_path = k.split('-')[1]
                try:
                    post = Post.objects.get(pk=pk_or_file_path)
                    if v == 'publish' or v == 'update':
                        self._publish(post)
                    elif v == 'unpublish':
                        self._unpublish(post)
                except ValueError:
                    if v == 'process':
                        try:
                            self._process(pk_or_file_path)
                        except ExternalError as e:
                            return self.render(request, error=e.message)
        return self.render(request)


def post(request, post_id):
    try:
        p = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        raise Http404()
    return render_to_response('post.html', {
        'post': p
    })
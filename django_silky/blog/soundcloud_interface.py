import json
import soundcloud


class SoundcloudError(Exception):
    pass


class SoundcloudInterface(object):
    def __init__(self):
        super(SoundcloudInterface, self).__init__()
        self.client = soundcloud.Client(client_id='e28776ad98cf1518c1446f2c3324afb7',
                                        client_secret='f5bb5adef708f45edf4842afc081b9c8',
                                        username='mtford@gmail.com',
                                        password='woodyf123')

    def get(self, path):

        resp = self.client.get(path)
        if resp.status_code == 200:
            try:
                return json.loads(resp.raw_data)
            except ValueError as e:
                raise SoundcloudError('invalid json: %s' % e)
        else:
            raise SoundcloudError('status code: %s' % resp.status_code)


    def me(self):
        return self.get('/me')

    def activities(self):
        return self.get('/me/activities')['collection']

    def latest_track_share(self):
        for activity in self.activities():
            if activity['type'] == 'track':
                return activity
        return None
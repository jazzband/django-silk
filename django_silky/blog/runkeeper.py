import requests


class RunkeeperInterface(object):
    auth_header = 'Bearer 707a0a077c1340598b9ec3d413a652b7'

    def fitness_activity(self):
        r = requests.get('https://api.runkeeper.com/fitnessActivities',
                         headers={'Authorization': self.auth_header,
                                  'Accept': 'application/vnd.com.runkeeper.FitnessActivityFeed+json'})
        return r.json()['items']
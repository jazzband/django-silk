"""generate fake data for the example app"""
from example_app.models import Blind

__author__ = 'mtford'

def main():
    venetian = Blind.objects.create(name='Venetian', child_safe=False)
    roller = Blind.objects.create(name='Roller', child_safe=True)

if __name__ == '__main__':
    main()
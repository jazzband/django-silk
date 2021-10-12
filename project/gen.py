# -*- coding: utf-8 -*-
"""Generate fake data for the example app."""
from example_app.models import Blind


def main():
    """Perform the main function logic."""
    venetian = Blind.objects.create(name="Venetian", child_safe=False)
    roller = Blind.objects.create(name="Roller", child_safe=True)


if __name__ == "__main__":
    main()

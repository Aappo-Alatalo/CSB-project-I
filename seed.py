"""Set up the database with a few residents and reservations for local testing."""
import os
from datetime import date, timedelta

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saunavaraus.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.management import call_command

from bookings.models import Profile, Reservation


def run():
    call_command('migrate', verbosity=0)

    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'Sauna2026admin')

    residents = [
        ('liisa', 'kissa123', 'Liisa Virtanen', 'A 12', '040 1234567'),
        ('matti', 'kissa123', 'Matti Korhonen', 'B 7', '050 7654321'),
    ]
    for username, password, name, apartment, phone in residents:
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.save()
        Profile.objects.get_or_create(
            user=user,
            defaults={'full_name': name, 'apartment': apartment, 'phone': phone},
        )

    liisa = User.objects.get(username='liisa')
    matti = User.objects.get(username='matti')
    today = date.today()
    Reservation.objects.get_or_create(
        date=today + timedelta(days=2), slot='19-20',
        defaults={'user': liisa, 'note': 'Guests coming over, please leave the sauna clean'},
    )
    Reservation.objects.get_or_create(
        date=today + timedelta(days=3), slot='20-21',
        defaults={'user': matti, 'note': 'Long sauna evening'},
    )
    print('Seed complete.')


if __name__ == '__main__':
    run()

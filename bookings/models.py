from django.contrib.auth.models import User
from django.db import models

SLOT_CHOICES = [
    ('17-18', '17:00-18:00'),
    ('18-19', '18:00-19:00'),
    ('19-20', '19:00-20:00'),
    ('20-21', '20:00-21:00'),
    ('21-22', '21:00-22:00'),
]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    apartment = models.CharField(max_length=10)
    phone = models.CharField(max_length=30)

    def __str__(self):
        return '%s (%s)' % (self.full_name, self.apartment)


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    date = models.DateField()
    slot = models.CharField(max_length=5, choices=SLOT_CHOICES)
    note = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'slot')
        ordering = ['date', 'slot']

    def __str__(self):
        return '%s %s - %s' % (self.date, self.get_slot_display(), self.user.username)

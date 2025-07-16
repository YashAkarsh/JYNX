from django.core.management.base import BaseCommand
from jynxapp import models
import datetime

class Command(BaseCommand):
    help='Deletes the expired zigs according to their expiry date'

    def handle(self,*args, **kwargs):
        current_dateTime=datetime.datetime.now()
        expired_zigs=models.Zig.objetcs.filter(expiry_date__lt=current_dateTime)
        expired_zigs.delete()
        print('kkkk')

        self.stdout.write(self.style.SUCCESS('Successfully deleted expired objects'))
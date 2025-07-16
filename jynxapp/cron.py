from django_cron import CronJobBase,Schedule
from . import models
from django.utils import timezone
import datetime
from background_task import background

class DeleteZigsCronJob(CronJobBase):
    RUN_EVERY_MIN=1/60
    schedule=Schedule(run_every_mins=RUN_EVERY_MIN)
    code = 'jynx.delete_zigs'

    def do(self):
        # from django.core.management import call_command
        # call_command('delete_expired_zigs')
        print('initiating zig delete cron job')
        models.Zig.objects.filter(expiry_date__lt=datetime.datetime.now()).delete()
        print('success')
        

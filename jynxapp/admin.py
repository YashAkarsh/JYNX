from django.contrib import admin
from . import models
# Register your models here.
class ReplyInline(admin.TabularInline):
    model = models.Replie
    extra = 0  # Number of empty forms to display
    fields = ['sender','content']

class ZigAdmin(admin.ModelAdmin):
    inlines = [ReplyInline]

admin.site.register(models.UserData)
admin.site.register(models.Zig,ZigAdmin)
admin.site.register(models.Replie)
admin.site.register(models.Notification)
admin.site.register(models.Report)




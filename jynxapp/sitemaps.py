from django.contrib import sitemaps
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import UserData, Zig


class StaticSitemap(Sitemap):

    changefreq = "daily"
    priority = 0.9

    def items(self):
        # Return list of url names for views to include in sitemap
       return ['about','help', 'tandc','signup','login','landing','meetdevs','discover','homepage','contact','privacypolicy']
    def location(self, item):
        return reverse(item)
    
class UserDataSitemap(sitemaps.Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return UserData.objects.all()

class ZigSitemap(sitemaps.Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Zig.objects.all()




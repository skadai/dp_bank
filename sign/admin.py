from django.contrib import admin
from sign.models import Event, Guest



class EventAdmin(admin.ModelAdmin):
    list_display = ['name','status','start_time','id']
    search_fields = ['name']
    list_filter = ['status']

class GuestAdmin(admin.ModelAdmin):
    list_display = ['realname','phone','email','sign','event']



# Register your models here.
admin.site.register(Event,EventAdmin)
admin.site.register(Guest,GuestAdmin)
from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import User
from .models import Location, Species, Refined_Sighting, Raw_Sighting, Expert_Ratification_Sightings

admin.site.register(Location)
admin.site.register(Species)
admin.site.register(Refined_Sighting)
admin.site.register(Raw_Sighting)
admin.site.register(Expert_Ratification_Sightings)

class MembershipInline(admin.TabularInline):
    model = Raw_Sighting.voted_by.through


class RawAdmin(admin.ModelAdmin):
    inlines = [
        MembershipInline,
    ]
    exclude = ('voted_by',)

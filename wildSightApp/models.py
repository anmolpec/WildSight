from django.db import models
from django.contrib.auth.models import User

#Create your models here.
# class UserProfile(models.Model):
#     user   = models.OneToOneField(User, on_delete=models.CASCADE)
#     avatar = models.ImageField(upload_to = 'avatars/')

class Location(models.Model):
    x_coordinate_start=models.DecimalField(max_digits=9, decimal_places=6)
    x_coordinate_end=models.DecimalField(max_digits=9, decimal_places=6)
    y_coordinate_start=models.DecimalField(max_digits=9, decimal_places=6)
    y_coordinate_end=models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return "Location centred at: {}, {}".format((self.x_coordinate_start+self.x_coordinate_end)/2, (self.y_coordinate_start+self.y_coordinate_end)/2 )

class Species(models.Model):
    
    class Meta:
        verbose_name_plural="Species"

    common_name=models.CharField(max_length=50)
    scientific_name=models.CharField(max_length=50)
    image = models.ImageField(blank = True, upload_to='Species_Images/')

    def __str__(self):
        return self.common_name


class Refined_Sighting(models.Model):
    MONTH_CHOICES=[
        (1,"January"),
        (2,"February"),
        (3,"March"),
        (4,"April"),
        (5,"May"),
        (6,"June"),
        (7,"July"),
        (8,"August"),
        (9,"September"),
        (10,"October"),
        (11,"November"),
        (12,"December"),
    ]

    time_period=models.IntegerField(choices=MONTH_CHOICES)

    Location=models.ForeignKey('Location', on_delete=models.CASCADE)

    Species=models.ForeignKey('Species', on_delete=models.CASCADE)

    Count=models.PositiveIntegerField(default=0)

    Number_of_sightings=models.PositiveIntegerField(default=0)

    def __str__(self):
        return "{} AT {} IN {}".format(self.Species, self.Location, self.get_time_period_display())


class Raw_Sighting(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)
    species = models.ForeignKey(Species,on_delete=models.CASCADE,null=True,blank=True)
    new_species = models.CharField(max_length=100,blank=True,null=True)
    date_time = models.DateTimeField()
    image = models.ImageField(max_length=256, blank = True, upload_to='uploads/')
    location_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    credible = models.BooleanField(default=False, blank=True)
    voted_by=models.ManyToManyField(User, related_name="Voter")

 
#INBUILT USER MODEL USED
#Fields:
#id
#username
#email
#password

#Temp Token table
#token
#userid

class Expert_Ratification_Sightings(Raw_Sighting):
    expert_credible=models.BooleanField(default=False, blank=True)

    def __str__(self):
        return "{} AT {}, {}. ON {}".format(self.new_species, self.location_latitude, self.location_longitude, self.date_time)

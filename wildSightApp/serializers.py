from rest_framework import serializers,generics
from .models import Species, Refined_Sighting, Location ,Raw_Sighting #, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username','first_name','last_name','email')

# class UserProfileSerializer(serializers.ModelSerializer):

#     class Meta(UserSerializer.Meta):
#         model = UserProfile
#         fields = UserSerializer.Meta.fields + ('avatar',)

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username','email','password')
        extra_kwargs = {'password':{'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])
        return user

#Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and  user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        fields=(
            'id',
            'common_name',
            'scientific_name',
            'image',
        )
        model=Species

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        fields=(
            'id',
            'x_coordinate_start',
            'x_coordinate_end',
            'y_coordinate_start',
            'y_coordinate_end',
        )
        model=Location

class Refined_Sighting_Serializer(serializers.ModelSerializer):
    class Meta:
        fields=(
            'id',
            'Species',
            'Location',
            'time_period',
            'Count',
            'Number_of_sightings',
        )
        model=Refined_Sighting

class Raw_Sighting_Serializer(serializers.ModelSerializer):
    class Meta:
        fields=(
            'user',
            'count',
            'species',
            'new_species',
            'date_time',
            'location_longitude',
            'location_latitude',
            'image',
            'credible',
        )
        model=Raw_Sighting

class Raw_Sighting_Serializer_Output(serializers.ModelSerializer):
    class Meta:
        fields=(
            'id',
            'user',
            'count',
            'species',
            'new_species',
            'date_time',
            'location_longitude',
            'location_latitude',
            'image',
            'voted_by',
            'credible',
            'upvotes',
            'downvotes'
        )
        model=Raw_Sighting
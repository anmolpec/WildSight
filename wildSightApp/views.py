from django.shortcuts import render
from .models import Species, Refined_Sighting, Location, Raw_Sighting, Expert_Ratification_Sightings #, UserProfile
from .serializers import SpeciesSerializer, Refined_Sighting_Serializer, Raw_Sighting_Serializer, LocationSerializer, UserSerializer, RegisterSerializer, LoginSerializer , Raw_Sighting_Serializer_Output#, UserProfileSerializer
from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from knox.models import AuthToken
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import json

# Create your views here.

class Species_list(generics.ListAPIView):
    queryset=Species.objects.all()
    serializer_class=SpeciesSerializer
    filter_backends=[filters.SearchFilter]
    search_fields=['common_name']

class Locations_list(generics.ListAPIView):
    #queryset=Location.objects.all()
    serializer_class=LocationSerializer

    def get_queryset(self):
        queryset=Location.objects.all()
        latitude=(self.request.query_params.get('lat'))
        longitude=(self.request.query_params.get('long'))
        if latitude is None and longitude is None:
            return queryset
        queryset=Location.objects.filter(y_coordinate_start__lt=latitude, y_coordinate_end__gte = latitude, x_coordinate_start__lt=longitude, x_coordinate_end__gte=longitude)
        return queryset

class Refined_Sightings_list(generics.ListAPIView):
    queryset=Refined_Sighting.objects.all()
    serializer_class=Refined_Sighting_Serializer

class Species_element(generics.RetrieveAPIView):
    queryset=Species.objects.all()
    serializer_class=SpeciesSerializer

class Refined_Sightings_Species_list(generics.ListAPIView):
    serializer_class=Refined_Sighting_Serializer

    def get_queryset(self):
        queryset=Refined_Sighting.objects.all()
        sp=self.request.query_params.get('sp')
        time=self.request.query_params.get('time')
        if time is None:
            return queryset.filter(Species=sp)
        return queryset.filter(Species=sp, time_period=time)
    

class Refined_Sightings_Locations_list(generics.ListAPIView):
    serializer_class=Refined_Sighting_Serializer

    def get_queryset(self):
        queryset=Refined_Sighting.objects.all()
        loc=self.request.query_params.get('loc')
        time=self.request.query_params.get('time')
        if time is None:
            return queryset.filter(Location=loc)
        return queryset.filter(Location=loc, time_period=time)

class Refined_Sightings_Species_Locations_list(generics.ListAPIView):
    serializer_class=Refined_Sighting_Serializer

    def get_queryset(self):
        queryset=Refined_Sighting.objects.all()
        loc=self.request.query_params.get('loc')
        time=self.request.query_params.get('time')
        sp=self.request.query_params.get('sp')
        if time is None:
            return queryset.filter(Location=loc)
        return queryset.filter(Location=loc, time_period=time, Species=sp)

class Location_element(generics.RetrieveAPIView):
    queryset=Location.objects.all()
    serializer_class=LocationSerializer

class Raw_Sighting_Input(generics.CreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    parser_classes = [MultiPartParser, FormParser]
    
    serializer_class = Raw_Sighting_Serializer

    def get_serializer(self, *args, **kwargs):
        # leave this intact
        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()
        """
        Intercept the request and see if it needs tweaking
        """        
        # Copy and manipulate the request
        draft_request_data = self.request.data.copy()
        draft_request_data["user"] = User.objects.get(username=draft_request_data["user"]).pk
        if Species.objects.filter(common_name=draft_request_data["species"]).exists():
            draft_request_data["species"] = Species.objects.get(common_name = draft_request_data["species"]).id
        else:
            draft_request_data["new_species"]=draft_request_data["species"]
            draft_request_data["species"]= "" 

        kwargs["data"] = draft_request_data
        return serializer_class(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        obj1=self.get_serializer(data=request.data)
        obj1.is_valid()
        # print(obj1.validated_data)
        #obj.create(validated_data=obj.validated_data)
        obj=obj1.save()
        if obj.credible==True:
            loc=Location.objects.get(y_coordinate_start__lt=obj.location_latitude, y_coordinate_end__gte =obj.location_latitude, x_coordinate_start__lt=obj.location_longitude, x_coordinate_end__gte=obj.location_longitude)
            sp=Species.objects.get(common_name=obj.species)
            time=obj.date_time.month
            try:
                refined=Refined_Sighting.objects.get(Location=loc,Species=sp,time_period=time)
                refined.Number_of_sightings+=1
                refined.Count+=obj.count
                refined.save()
            except Refined_Sighting.DoesNotExist:
                refined=Refined_Sighting(Location=loc, Species=sp, time_period=time, Count=obj.count, Number_of_sightings=1)
                refined.save()
        headers = self.get_success_headers(obj1.data)
        return Response(obj1.data, status=status.HTTP_201_CREATED, headers=headers)

    queryset = Raw_Sighting.objects.all()
        
class Raw_Sighting_Output(generics.ListAPIView):
    serializer_class = Raw_Sighting_Serializer_Output
    queryset = Raw_Sighting.objects.all()
   

#Register API

class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user,context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })

# Login API
class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer
    authentication_classes = [BasicAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response({
            "user": UserSerializer(user,context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })

#Get user API
class GetUserSightings(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class=Raw_Sighting_Serializer

    def get_queryset(self):
        user=self.request.user
        queryset=Raw_Sighting.objects.filter(user = user)
        num=self.request.query_params.get('num')
        if num is not None:
            return queryset.order_by('date_time').reverse()[0:int(num)]
        return queryset

class UserProfileAPI(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if('password' in body):
            self.request.user.set_password(body['password'])
            self.request.user.save()
        return self.update(request, *args, **kwargs)

    


class Ratification_List(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class=Raw_Sighting_Serializer_Output

    def get_queryset(self):
        queryset=Raw_Sighting.objects.filter(credible=False)
        user=self.request.user
        queryset=queryset.exclude(user=user)
        queryset = queryset.exclude(voted_by=user)    
        num=self.request.query_params.get('num') or 10
        num = int(num)
        skip = self.request.query_params.get('skip') or 0
        skip = int(skip)
        return queryset.order_by('date_time')[skip*num:(skip+1)*num]


class vote(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class=Raw_Sighting_Serializer_Output

    def get_queryset(self):
        #####add this user vote to many to one relationship
        pk=int(self.request.query_params.get('pk'))
        obj=Raw_Sighting.objects.get(pk=pk)

        if obj is None:
            return JsonResponse(code=400, data="wrong parameters")
    
        obj.voted_by.add(self.request.user)

        votestr=self.request.query_params.get('vote')
        if votestr=='up':
            obj.upvotes+=1
        elif votestr=='down':
            obj.downvotes+=1
        
        obj.save()
        if obj.upvotes+obj.downvotes>=10:
            if obj.upvotes/max(1,obj.downvotes) >= 0.7:
                #####add this to refined sighting , make credibility=true  
                obj.credible=True
                obj.save()
                if obj.species is not None:
                    loc=Location.objects.get(y_coordinate_start__lt=obj.location_latitude, y_coordinate_end__gte =obj.location_latitude, x_coordinate_start__lt=obj.location_longitude, x_coordinate_end__gte=obj.location_longitude)
                    sp=Species.objects.get(common_name=obj.species)
                    time=obj.date_time.month
                    try:
                        refined=Refined_Sighting.objects.get(Location=loc,Species=sp,time_period=time)
                        refined.Number_of_sightings+=1
                        refined.Count+=obj.count
                        refined.save()
                    except Refined_Sighting.DoesNotExist:
                        refined=Refined_Sighting(Location=loc, Species=sp, time_period=time, Count=obj.count, Number_of_sightings=1)
                        refined.save()
                else:
                    expert_obj=Expert_Ratification_Sightings()
                    expert_obj.__dict__.update(obj.__dict__)
                    expert_obj.save()

        queryset=Raw_Sighting.objects.filter(pk=pk)
        return queryset
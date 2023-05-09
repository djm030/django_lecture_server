from rest_framework import serializers
from .models import Instructor_Application
from images.serializers import ImageSerializer
from users.serializers import InstructorSerializer

class InstructorApplicationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')
    title = serializers.CharField(source='career')
    author = serializers.CharField(source='user.name')
    date = serializers.DateTimeField(source='created_at', format='%Y-%m-%d')
    introduction = serializers.CharField(source='description')
    img = serializers.ImageField(source='image')
    isDone = serializers.SerializerMethodField()
   
    
    
    def get_isDone(self, obj):
        return None
    
    class Meta:
        model = Instructor_Application
        fields = ("id", "title", "author", "date", "introduction", "img","isDone")
        
    
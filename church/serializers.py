from rest_framework import serializers
from .models import Service, AccountDetail, Lyric, Sermon, UserSubmission

class AccountDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountDetail
        fields = ['id', 'account_type', 'account_name', 'account_number', 'bank_name']

class LyricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lyric
        fields = ['id', 'title', 'content']

class SermonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sermon
        fields = ['id', 'title', 'date_preached', 'notes_or_link']

class ServiceSerializer(serializers.ModelSerializer):
    accounts = AccountDetailSerializer(many=True, read_only=True)
    lyrics = LyricSerializer(many=True, read_only=True)
    sermons = SermonSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'name', 'day_of_week', 'logo', 'theme_color', 
            'tiktok_url', 'instagram_url', 'youtube_url', 'twitter_url', 'whatsapp_url',
            'accounts', 'lyrics', 'sermons'
        ]

class UserSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubmission
        fields = ['id', 'submission_type', 'content', 'image', 'is_approved', 'created_at']
        read_only_fields = ['is_approved', 'created_at']

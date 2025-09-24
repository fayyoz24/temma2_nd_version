
from rest_framework import serializers
from django.utils import timezone
from .models import NewsArticle, UserNewsView, Author, Language, ArticleVersion

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name', 'code']

class ArticleVersionSerializer(serializers.ModelSerializer):
    # language_code = serializers.CharField(source='language.code', read_only=True)
    language = LanguageSerializer()
    class Meta:
        model = ArticleVersion
        fields = ['id', 'title', 'content', 'difficulty_level', 'language']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"

class NewsArticleCreateUpdateSerializer(serializers.ModelSerializer):
    website_link = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    scheduled_for = serializers.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%S.%f', 
                      '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S'],
        required=False, allow_null=True
    )
    versions = ArticleVersionSerializer(many=True, required=False)

    class Meta:
        model = NewsArticle
        fields = ['id', 'original_title', 'original_content', 'scheduled_for', 
                 'website_link', 'author', 'original_language', 'versions']

    def validate_scheduled_for(self, value):
        if value and (value < timezone.now()):
            raise serializers.ValidationError("Cannot schedule article in the past")
        return value

    def create(self, validated_data):
        versions_data = validated_data.pop('versions', [])
        article = NewsArticle.objects.create(**validated_data)
        
        for version_data in versions_data:
            ArticleVersion.objects.create(article=article, **version_data)
        
        return article

class NewsArticleDetailByLanguageSerializer(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField()
    is_seen = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    scheduled_for = serializers.DateTimeField()
    is_published = serializers.BooleanField(read_only=True)
    author = AuthorSerializer(read_only=True)
    original_language = LanguageSerializer(read_only=True)
    versions = ArticleVersionSerializer(many=True, read_only=True)
    viewed_at = serializers.DateTimeField(source='usernewsview.viewed_at', read_only=True)

    class Meta:
        model = NewsArticle
        fields = ['id', 'original_title', 'original_content', 'website_link', 
                  'is_read',
                 'created_at', 'is_seen', 'scheduled_for', 'is_published', 
                 'author', 'original_language', 'versions', 'viewed_at']

    def get_is_read(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
            
        # Check if this article has been viewed by the user
        return UserNewsView.objects.filter(
            user=request.user,
            article=obj
        ).exists()


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        
        if request and request.user.is_authenticated:
            user_news_view = UserNewsView.objects.filter(
                article=instance, 
                user=request.user
            ).first()
            representation['viewed_at'] = user_news_view.viewed_at if user_news_view else None

            # Get requested language version if specified
            language_code = request.query_params.get('language')
            difficulty = request.query_params.get('difficulty', 'medium')
            
            if language_code:
                version = instance.get_version(language_code, difficulty)
                if version:
                    representation['title'] = version.title
                    representation['content'] = version.content
                    representation['current_version'] = ArticleVersionSerializer(version).data

        return representation

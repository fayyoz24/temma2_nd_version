from rest_framework.serializers import ModelSerializer, Serializer, StringRelatedField, SlugRelatedField
from rest_framework import serializers
from .models import(
    Category,
    Question,
    Answer,#Student,
    #MentorMatchScholierTest, MentorForScholierTest
)
from users.serializers import UserSerializer


class CategoryCreateSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def create(self, validated_data):
        # Add user_id to the validated data if a user is authenticated
        if self.context['request'].user.is_authenticated:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class QuestionCreateSerializer(ModelSerializer):
    # categories = SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='name'
    # )
    is_anonymous = serializers.BooleanField(default=False)
    class Meta:
        model=Question
        
        fields=['id', 'title', 'detail','categories', 'email', 'is_anonymous']
        
    def update(self, instance, validated_data):
        # Check if instance exists (updating) or it's a new instance (creating)
        if instance:
            # Update the instance with the validated data
            instance = super().update(instance, validated_data)
            
            # Modify the 'enabled' field of the instance
            instance.is_enabled = True 
            
            # Save the instance
            instance.save()
        else:
            # Create a new instance without updating the 'type' field
            instance = Question.objects.create(**validated_data)
        
        return instance

class CategoryModelSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class QuestionAllGetSerializer(ModelSerializer):
    categories = CategoryModelSerializer(many=True, read_only=True)
    updated_by = StringRelatedField(read_only=True)
    class Meta:
        model=Question
        fields = '__all__'

class QuestionGetSerializer(ModelSerializer):
    categories = CategoryModelSerializer(many=True, read_only=True)
    updated_by = StringRelatedField(read_only=True)
    is_answered = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = '__all__'

    def get_is_answered(self, obj):
        """Check if the question has any answers"""
        return obj.answer_set.exists()

    def get_is_read(self, obj):
        """
        Return False if any answer is unread by the current user
        Return True if all answers have been read by the current user
        Return True if there are no answers yet
        """
        request = self.context.get('request')
        # if not request or not request.user.is_authenticated:
        #     return False
            
        answers = obj.answer_set.all()
        if not answers:
            return False  # No answers yet, so nothing to read
            
        # Print for debugging
        
        for answer in answers:
            
            # If current user hasn't read this answer
            if not answer.read_by.filter(id=request.user.id).exists():
                return False
                
        return True  # All answers have been read    

class AnswerCreateSerializer(ModelSerializer):
    question = StringRelatedField(read_only=True)
    class Meta:
        model=Answer
        fields=('question','detail')

    def create(self, validated_data):
        # Add user_id to the validated data if a user is authenticated
        if self.context['request'].user.is_authenticated:
            if self.context['request'].method=='POST':
                validated_data['answered_by'] = self.context['request'].user
                validated_data['updated_by'] = self.context['request'].user
            else:
                validated_data['updated_by'] = self.context['request'].user
        return super().create(validated_data)
    

class QuestionModelSerializer(ModelSerializer):
    class Meta:
        model = Question
        categories=CategoryModelSerializer(many=True, read_only=True)
        fields = ['id', 'title', 'detail', 'categories']

class QuestionModelCategorySerializer(ModelSerializer):
    categories = CategoryModelSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        categories=CategoryModelSerializer(many=True, read_only=True)
        fields = ['id', 'title', 'detail', 'categories']

class AnswerGetSerializer(ModelSerializer):
    question = QuestionModelCategorySerializer()  # Notice the parentheses to call it as a class
    answered_by = UserSerializer() #StringRelatedField(read_only=True)
    updated_by = StringRelatedField(read_only=True)

    class Meta:
        model = Answer
        fields = '__all__'

# class AnswerGetSerializer(serializers.ModelSerializer):
#     is_read = serializers.SerializerMethodField()
#     question = QuestionModelCategorySerializer()  # Notice the parentheses to call it as a class
#     answered_by = UserSerializer() #StringRelatedField(read_only=True)

#     class Meta:
#         model = Answer
#         fields = ['id', 'question', 'answered_by', 'created_at', 'updated_by', 'last_updated', 'detail', 'is_read']
    
#     def get_is_read(self, obj):
#         """
#         Returns whether the current user has read this answer
#         """
#         request = self.context.get('request')
#         if not request or not request.user.is_authenticated:
#             return False
#         return obj.is_read_by(request.user)

class QuestionCategorySerializer(ModelSerializer):
    categories = CategoryModelSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        categories=CategoryModelSerializer(many=True, read_only=True)
        fields = ['categories']

class AnswerCategorySerializer(ModelSerializer):
    question = QuestionModelCategorySerializer()  
    class Meta:
        model = Answer
        fields = ['question']

class QuestionUpdateSerializer(ModelSerializer):
    # categories = CategoryModelSerializer(many=True, read_only=True)
    # updated_by = StringRelatedField(read_only=True)
    class Meta:
        model=Question
        fields = '__all__'

class QuestionUpdateCategSerializer(Serializer):

    categ_name = serializers.CharField()

class QuestionCategoryResponseSerializer(serializers.ModelSerializer):
    categories = CategoryModelSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'title', 'categories']


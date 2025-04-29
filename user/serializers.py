from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Certificate, Education, Experience, Project, Service, Skill, User

class UserRegistrationSerializer(serializers.ModelSerializer):
    code = serializers.DictField(write_only=True, required=False, allow_null=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'phone_number', 'code']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        # Ensure that either email or phone_number is provided
        if not (data.get('email') or data.get('phone_number')):
            raise serializers.ValidationError("Either email or phone_number must be provided.")
        
        return data

    def create(self, validated_data):
        # Create a new user with hashed password
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email'),
            phone_number=validated_data.get('phone_number'),
            password=make_password(validated_data['password']),
            code=validated_data['code'],
        )
        return user

    def to_representation(self, instance):
        # Generate JWT token and include it in the response
        refresh = RefreshToken.for_user(instance)
        token_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return {
            'username': instance.username,
            'email': instance.email,
            'phone_number': instance.phone_number,
            'token': token_data,
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email', 'phone_number', 'code']



class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, required=False)
    certificates = CertificateSerializer(many=True, required=False)
    education = EducationSerializer(many=True, required=False)
    experience = ExperienceSerializer(many=True, required=False)
    projects = ProjectSerializer(many=True, required=False)
    services = ServiceSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone_number', 'profile_picture',
            'facial_recognition_image', 'about', 'status', 'last_seen',
            'code', 'contact_list', 'device_tokens', 'settings', 'blocked_users',
            'skills', 'certificates', 'education', 'experience', 'projects', 'services'
        ]

    def create(self, validated_data):
        # Pop nested fields
        skills_data = validated_data.pop('skills', [])
        certificates_data = validated_data.pop('certificates', [])
        education_data = validated_data.pop('education', [])
        experience_data = validated_data.pop('experience', [])
        projects_data = validated_data.pop('projects', [])
        services_data = validated_data.pop('services', [])

        # Create user
        user = User.objects.create(**validated_data)

        # Create related nested fields
        for skill in skills_data:
            Skill.objects.create(user=user, **skill)
        for cert in certificates_data:
            Certificate.objects.create(user=user, **cert)
        for edu in education_data:
            Education.objects.create(user=user, **edu)
        for exp in experience_data:
            Experience.objects.create(user=user, **exp)
        for proj in projects_data:
            Project.objects.create(user=user, **proj)
        for service in services_data:
            Service.objects.create(user=user, **service)

        return user

    def update(self, instance, validated_data):
        # Update basic user fields
        nested_fields = ['skills', 'certificates', 'education', 'experience', 'projects', 'services']
        for attr, value in validated_data.items():
            if attr not in nested_fields:
                setattr(instance, attr, value)
        instance.save()

        # Update nested relationships
        def update_nested(model, related_name, data):
            getattr(instance, related_name).all().delete()
            for item in data:
                model.objects.create(user=instance, **item)

        if 'skills' in validated_data:
            update_nested(Skill, 'skills', validated_data['skills'])
        if 'certificates' in validated_data:
            update_nested(Certificate, 'certificates', validated_data['certificates'])
        if 'education' in validated_data:
            update_nested(Education, 'education', validated_data['education'])
        if 'experience' in validated_data:
            update_nested(Experience, 'experience', validated_data['experience'])
        if 'projects' in validated_data:
            update_nested(Project, 'projects', validated_data['projects'])
        if 'services' in validated_data:
            update_nested(Service, 'services', validated_data['services'])

        return instance

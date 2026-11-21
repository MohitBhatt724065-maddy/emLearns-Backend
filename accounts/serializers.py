from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password as validate_django_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework import serializers

from .models import StudentProfile


class RegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        required=True
    )

    password2 = serializers.CharField(
        write_only=True,
        required=True
    )

    email = serializers.EmailField(
        required=True
    )

    institution = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True
    )

    academic_level = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "institution",
            "academic_level",
        ]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({
                "password2": "Passwords do not match."
            })

        user = User(
            username=attrs.get("username", ""),
            email=attrs.get("email", ""),
            first_name=attrs.get("first_name", ""),
            last_name=attrs.get("last_name", ""),
        )

        try:
            validate_django_password(attrs["password"], user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({
                "password": list(e.messages)
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):

        validated_data.pop("password2")

        institution = validated_data.pop("institution", "")
        academic_level = validated_data.pop("academic_level", "")

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        StudentProfile.objects.create(
            user=user,
            institution=institution,
            academic_level=academic_level
        )

        return user

class EmailOrUsernameTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        identifier = attrs.get(self.username_field, "")
        if "@" in identifier:
            user = User.objects.filter(email__iexact=identifier).first()
            if user:
                attrs[self.username_field] = user.get_username()
        return super().validate(attrs)


class MeSerializer(serializers.ModelSerializer):
    institution = serializers.CharField(source="student_profile.institution", read_only=True)
    academic_level = serializers.CharField(source="student_profile.academic_level", read_only=True)
    bio = serializers.CharField(source="student_profile.bio", read_only=True)
    profile_picture = serializers.ImageField(source="student_profile.profile_picture", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "institution", "academic_level", "bio", "profile_picture",
            "date_joined",
        ]
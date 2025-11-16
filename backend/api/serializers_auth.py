from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Trader


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm Password")
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2', 'first_name', 'last_name']
        read_only_fields = ['id']

    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({
                'password': 'Passwords do not match.'
            })
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({
                'email': 'This email address is already in use.'
            })
        
        return attrs

    def create(self, validated_data):
        """Create user and associated trader profile"""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # Create associated trader profile
        Trader.objects.create(user=user)
        
        return user


class UserLoginSerializer(TokenObtainPairSerializer):
    """Serializer for user login with additional claims"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        
        # Add trader profile info if exists
        if hasattr(user, 'trader_profile'):
            token['trader_id'] = user.trader_profile.id
            token['is_trader'] = True
        
        return token


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    trader_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'trader_profile']
        read_only_fields = ['id', 'date_joined']
    
    def get_trader_profile(self, obj):
        """Get trader profile if exists"""
        if hasattr(obj, 'trader_profile'):
            from .serializers import TraderSerializer
            return TraderSerializer(obj.trader_profile).data
        return None


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'old_password', 'new_password', 'new_password2']

    def validate(self, attrs):
        """Validate password change if provided"""
        if 'old_password' in attrs or 'new_password' in attrs:
            user = self.context['request'].user
            
            if not user.check_password(attrs.get('old_password', '')):
                raise serializers.ValidationError({
                    'old_password': 'Old password is incorrect.'
                })
            
            if attrs.get('new_password') != attrs.get('new_password2'):
                raise serializers.ValidationError({
                    'new_password': 'New passwords do not match.'
                })
        
        return attrs

    def update(self, instance, validated_data):
        """Update user and change password if provided"""
        # Handle password change
        if 'new_password' in validated_data:
            instance.set_password(validated_data.pop('new_password'))
            validated_data.pop('new_password2', None)
        
        # Remove old_password as it's not a model field
        validated_data.pop('old_password', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        """Validate passwords"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                'new_password': 'New passwords do not match.'
            })
        
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({
                'old_password': 'Old password is incorrect.'
            })
        
        return attrs

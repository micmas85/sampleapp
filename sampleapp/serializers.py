from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import WorkOrder

MIN_TITLE_LENGTH = 5
MIN_BODY_LENGTH = 10

class RegistrationSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def save(self):

        user = User(
            email=self.validated_data['email'],
            username=self.validated_data['username']
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError(
                {'password': 'Passwords must match.'})
        user.set_password(password)
        user.save()
        return user


class AccountPropertiesSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['pk', 'email', 'username', ]


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)


class WorkOrderSerializer(serializers.ModelSerializer):
	created_by = serializers.SerializerMethodField()
	assigned_to = serializers.SerializerMethodField()

	def get_created_by(self, obj):
		return obj.created_by.username

	def get_assigned_to(self, obj):
		return obj.assigned_to.username

	class Meta:
		model = WorkOrder
		fields = ['pk', 'title', 'description', 'status', 'created_by', 'created_at', 'updated_at' , 'assigned_to']
  
class WorkOrderUpdateSerializer(serializers.ModelSerializer):

	class Meta:
		model = WorkOrder
		fields = ['status']
  
class WorkOrderCreateSerializer(serializers.ModelSerializer):

	class Meta:
		model = WorkOrder
		fields = ['title', 'description' ]

	def save(self):
		
		try:
			title = self.validated_data['title']
			if len(title) < MIN_TITLE_LENGTH:
				raise serializers.ValidationError({"response": "Enter a title longer than " + str(MIN_TITLE_LENGTH) + " characters."})
			
			description = self.validated_data['description']
			if len(description) < MIN_BODY_LENGTH:
				raise serializers.ValidationError({"response": "Enter a description longer than " + str(MIN_BODY_LENGTH) + " characters."})

			work_order = WorkOrder(
								title=title,
								description=description
								)

			work_order.save()
			return work_order
		except KeyError:
			raise serializers.ValidationError({"response": "You must have a title and some description."})


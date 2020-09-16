from rest_framework import status, generics, viewsets
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import update_session_auth_hash
from .models import WorkOrder
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, BadHeaderError
from rest_framework.generics import UpdateAPIView
from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django.conf import settings

SUCCESS = 'success'
ERROR = 'error'
DELETE_SUCCESS = 'Deleted'
UPDATE_SUCCESS = 'Updated'
CREATE_SUCCESS = 'Created'

def index(request):
    return render(request, 'sampleapp/index.html')

# Register
@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def registration_view(request):

    if request.method == 'POST':
        data = {}
        email = request.data.get('email', '0').lower()
        if validate_email(email) != None:
            data['error_message'] = 'That email is already in use.'
            data['response'] = 'Error'
            return Response(data)

        username = request.data.get('username', '0')
        if validate_username(username) != None:
            data['error_message'] = 'That username is already in use.'
            data['response'] = 'Error'
            return Response(data)

        serializer = RegistrationSerializer(data=request.data)
        print(serializer)

        if serializer.is_valid():
            user = serializer.save()
            data['response'] = 'successfully registered new user.'
            data['email'] = user.email
            data['username'] = user.username
            data['pk'] = user.pk
            token = Token.objects.get(user=user).key
            data['token'] = token
        else:
            data = serializer.errors
        return Response(data)


def validate_email(email):
    user = None
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None
    if user != None:
        return email


def validate_username(username):
    user = None
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return None
    if user != None:
        return username


# Account properties
# Headers: Authorization: Token <token>
@api_view(['GET', ])
@permission_classes((IsAuthenticated, ))
def account_properties_view(request):

    try:
        user = request.user
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AccountPropertiesSerializer(user)
        return Response(serializer.data)


# Account update properties
# Headers: Authorization: Token <token>
@api_view(['PUT', ])
@permission_classes((IsAuthenticated, ))
def update_account_view(request):

    try:
        user = request.user
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = AccountPropertiesSerializer(user, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['response'] = 'User update success'
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObtainAuthTokenView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        context = {}

        email = request.POST.get('username')
        password = request.POST.get('password')
        user = User.objects.get(email=email)
        username = user.username
        user = authenticate(username=username, password=password)
        if user:
            try:
                token = Token.objects.get(user=user)
            except Token.DoesNotExist:
                token = Token.objects.create(user=user)
            context['response'] = 'Successfully authenticated.'
            context['pk'] = user.pk
            context['email'] = email.lower()
            context['token'] = token.key
        else:
            context['response'] = 'Error'
            context['error_message'] = 'Invalid credentials'

        return Response(context)


@api_view(['GET', ])
@permission_classes([])
@authentication_classes([])
def does_account_exist_view(request):

    if request.method == 'GET':
        email = request.GET['email'].lower()
        data = {}
        try:
            user = User.objects.get(email=email)
            data['response'] = email
        except User.DoesNotExist:
            data['response'] = "User does not exist"
        return Response(data)


class ChangePasswordView(UpdateAPIView):

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            # confirm the new passwords match
            new_password = serializer.data.get("new_password")
            confirm_new_password = serializer.data.get("confirm_new_password")
            if new_password != confirm_new_password:
                return Response({"new_password": ["New passwords must match"]}, status=status.HTTP_400_BAD_REQUEST)

            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({"response": "successfully changed password"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def password_reset_request(request):
	context = {}
	if request.method == "POST":
		email = request.POST['email'].lower()
		associated_users = User.objects.filter(Q(email=email))
		if associated_users.exists():
			for user in associated_users:
				subject = "Password Reset Requested"
				email_template_name = "sampleapp/registration/password_reset_email.txt"
				c = {
				"email": user.email,
				'domain': 'michalmaslak-sampleapp.herokuapp.com',
					'site_name': 'Sample Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'https',
                    }
				email = render_to_string(email_template_name, c)
				try:
					send_mail(subject, email, settings.EMAIL_HOST_USER,
								[user.email], fail_silently=False)
					context['response'] = 'Success'
				except BadHeaderError:
					context['response'] = 'Error'
					context['error_message'] = 'Invalid header found'
				return Response(context)
			else:
				context['response'] = 'Error'
				context['error_message'] = 'User with'
				return Response(context)
		else:
			context['response'] = 'Error'
			context['error_message'] = 'User with email: '+email+' does not exist.'
			return Response(context)

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer


class WorkOrderListView(ListAPIView):
    serializer_class = WorkOrderSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('title', 'description', 'created_by__username')

    def get_queryset(self):
        return WorkOrder.objects.all().filter(assigned_to=self.request.user).exclude(status__in=['COMPLETED','CANCELLED'])
    
@api_view(['GET', ])
@permission_classes((IsAuthenticated, ))
def detail_work_order(request, pk):

	try:
		work_order = WorkOrder.objects.get(pk=pk)
	except WorkOrder.DoesNotExist:
		return Response(status=status.HTTP_404_NOT_FOUND)

	if request.method == 'GET':
		serializer = WorkOrderSerializer(work_order)
		return Response(serializer.data)

@api_view(['PUT',])
@permission_classes((IsAuthenticated,))
def update_work_order(request, pk):

    try:
        work_order = WorkOrder.objects.get(pk=pk)
    except WorkOrder.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = WorkOrderUpdateSerializer(work_order, data=request.data, partial=True)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['response'] = UPDATE_SUCCESS
            data['pk'] = work_order.pk
            data['title'] = work_order.title
            data['description'] = work_order.description
            data['status'] = work_order.status
            data['created_by'] = None
            if(work_order.created_by != None):
                data['created_by'] = work_order.created_by.username
            data['created_at'] = work_order.created_at
            data['updated_at'] = work_order.updated_at
            data['assigned_to'] = None
            if(work_order.assigned_to != None):
                data['assigned_to'] = work_order.assigned_to.username    
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE',])
@permission_classes((IsAuthenticated, ))
def delete_work_order(request, pk):

	try:
		work_order = WorkOrder.objects.get(pk=pk)
	except WorkOrder.DoesNotExist:
		return Response(status=status.HTTP_404_NOT_FOUND)

	user = request.user
	if work_order.created_by != user:
		return Response({'response':"You don't have permission to delete that."}) 

	if request.method == 'DELETE':
		operation = work_order.delete()
		data = {}
		if operation:
			data['response'] = DELETE_SUCCESS
		return Response(data=data)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def create_work_order(request):

    if request.method == 'POST':
        data = request.data
        serializer = WorkOrderCreateSerializer(data=data)
        user = User.objects.get(username=request.user.username)
        data = {}
        if serializer.is_valid():
            work_order = serializer.save()
            work_order.created_by=user
            work_order.assigned_to=user
            work_order.save()
            data['response'] = CREATE_SUCCESS
            data['pk'] = work_order.id
            data['title'] = work_order.title
            data['description'] = work_order.description
            data['status'] = work_order.status
            data['created_by'] = work_order.created_by.username
            data['created_at'] = work_order.created_at
            data['updated_at'] = work_order.updated_at
            data['assigned_to'] = work_order.assigned_to.username
            if(work_order.assigned_to!=None):
                data['assigned_to'] = work_order.assigned_to.username                    
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def is_creator_of_work_order(request, pk):
	try:
		work_order = WorkOrder.objects.get(pk=pk)
	except WorkOrder.DoesNotExist:
		return Response(status=status.HTTP_404_NOT_FOUND)

	data = {}
	user = request.user
	if work_order.created_by != user:
		data['response'] = "You don't have permission to edit that."
		return Response(data=data)
	data['response'] = "You have permission to edit that."
	return Response(data=data)
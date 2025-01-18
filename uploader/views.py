from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from .models import TxtFile
from .serializers import TxtFileSerializer, TxtFileDetailSerializer, TxtFileCreateSerializer
# Create your views here.

import tempfile
from .utils import download_file_from_s3
import os

from django.shortcuts import HttpResponse
from wsgiref.util import FileWrapper

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500

class FilesView(APIView):
    paginator = LargeResultsSetPagination()

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'GET':
            serializer = TxtFileSerializer
        elif self.request.method == 'POST':
            serializer = TxtFileCreateSerializer
        else:
            raise MethodNotAllowed(self.request.method)
        
        return serializer(*args, **kwargs, context={"request": self.request})

    def get_queryset(self, *args, **kwargs):
        files = TxtFile.objects.filter(user=self.request.user).order_by("created_at")
        return files

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginator.paginate_queryset(queryset, request, view=self)
        serializer = self.get_serializer(page, many=True)
        return self.paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        return Response(serializer.errors)


class FileDetailView(APIView):
    paginator = LargeResultsSetPagination()

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'GET':
            serializer = TxtFileDetailSerializer
        elif self.request.method == 'DELETE':
            serializer = TxtFileCreateSerializer
        else:
            raise MethodNotAllowed(self.request.method)
        
        return serializer(*args, **kwargs, context={"request": self.request})

    def get_queryset(self, *args, **kwargs):
        uuid = kwargs.get('uuid')
        file = TxtFile.objects.filter(uuid=uuid, archived=False).first()
        return file

    def get(self, request, *args, **kwargs):
        file = self.get_queryset(*args, **kwargs)
        serializer = self.get_serializer(file)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        file = self.get_queryset(*args, **kwargs)
        file.delete()

        return Response({"message": "file deleted."})
    
class FileDownloadView(APIView):
    paginator = LargeResultsSetPagination()

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'GET':
            serializer = TxtFileDetailSerializer
        elif self.request.method == 'DELETE':
            serializer = TxtFileCreateSerializer
        else:
            raise MethodNotAllowed(self.request.method)
        
        return serializer(*args, **kwargs, context={"request": self.request})

    def get_queryset(self, *args, **kwargs):
        uuid = kwargs.get('uuid')
        file = TxtFile.objects.filter(uuid=uuid, archived=False).first()
        return file

    def get(self, request, *args, **kwargs):
        file_obj = self.get_queryset(*args, **kwargs)
        obj_key = file_obj.file_path
        
        try:
            with tempfile.TemporaryDirectory(file_obj.uuid) as temp_dir:
                
                save_path = os.path.join(temp_dir, file_obj.file_name)
                download_file_from_s3(obj_key, save_path)
                loc = os.path.join(temp_dir, file_obj.file_name)

                with open(loc, 'rb') as f:
                    response = HttpResponse(FileWrapper(f), content_type='text/plain')
                    response['Content-Disposition'] = f'attachment; filename="{file_obj.file_name}"'
                    
                    return response
    
        except:
            return Response({"error": "cannot download file"}, status=status.HTTP_410_GONE)
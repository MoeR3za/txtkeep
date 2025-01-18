import os
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import  AccessToken
from django.core.files.uploadedfile import SimpleUploadedFile

from uploader.models import TxtFile

User = get_user_model() 

def upload_test_file(file_name: str) -> dict:
    with open(f'uploader/test_files/{file_name}', 'rb') as f:
        file_content = f.read()
        file = SimpleUploadedFile(file_name, file_content, content_type='text/plain')
        data = {
            'files': [file]
        }
        
        return data

def generate_test_file_data(file_name: str, username: str) -> dict:
    f_path = f'uploader/test_files/{file_name}'
    with open(f_path, 'rb') as f:
        file_content = f.read()
        # Prepare the data to be sent in the POST request
        data = {
            'file_name': file_name,
            'file_size': os.path.getsize(f_path),
            'file_content': file_content,
            'file_path': f"uploads/{username}/{file_name}",
        }
        
        return data

class MyFileViewSetTest(APITestCase):
    def setUp(self):
        self.email = 'test@example.com'
        self.username = 'username'
        self.password = 'pa$$word'
        self.first_name = "John"
        self.last_name = "Doe"
        self.user = User.objects.create_user(
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            username=self.username,
            password=self.password
        )
        self.access_token = str(AccessToken.for_user(self.user))
        
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.access_token
        )
        
    def test_uploading_new_file(self):
        url = '/api/files/'        
        file_name = "file_ok.txt"
        data = upload_test_file(file_name)

        response = self.client.post(url, data=data)
        resp_content = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert file name in the saved_files
        self.assertEqual(resp_content['saved_files'][0]['file_name'], file_name)
        

    def test_uploading_small_file(self):
        url = '/api/files/'
        file_name = "file_small.txt"
        data = upload_test_file(file_name)

        response = self.client.post(url, data=data)
        resp_content = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_content['invalid_files'][0]['file_name'], file_name) 

    def test_uploading_big_file(self):
        url = '/api/files/'
        file_name = "file_big.txt"
        data = upload_test_file(file_name)

        response = self.client.post(url, data=data)
        resp_content = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_content['invalid_files'][0]['file_name'][:len(file_name)], file_name) 

    def test_uploading_nontext_file(self):
        url = '/api/files/'
        file_name = "file_noext"
        data = upload_test_file(file_name)

        response = self.client.post(url, data=data)
        resp_content = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_content['invalid_files'][0]['file_name'][:len(file_name)], file_name) 


    def test_get_files(self):
        url = '/api/files/'
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

    def test_get_file(self):
        file_name = "file_ok.txt"
        test_file_data = generate_test_file_data(file_name, self.user.username)
        creation_data = {
            'user': self.user,
            **test_file_data,
            'file_path': f"uploads/{self.user.username}/{file_name}"
        }

        file = TxtFile.objects.create(
            **creation_data
        )

        url = f'/api/files/{file.uuid}/'
        response = self.client.get(url)
        resp_content = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_content['file_name'], creation_data['file_name'])


    def test_delete_myfile(self):
        file_name = "file_ok.txt"
        test_file_data = generate_test_file_data(file_name, self.user.username)
        creation_data = {
            'user': self.user,
            **test_file_data,
        }

        file = TxtFile.objects.create(
            **creation_data
        )
        
        url = f'/api/files/{file.uuid}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
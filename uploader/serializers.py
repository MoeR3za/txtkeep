from rest_framework import serializers
from uploader.models import TxtFile

import os

from django.core.files.storage import default_storage
from django.conf import settings

from mimetypes import guess_type
from .models import TxtFile


class TxtFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TxtFile
        fields = [
            'uuid',
            'file_name',
            'file_size',
            'created_at']

class TxtFileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TxtFile
        fields = [
            'uuid',
            'file_name',
            'file_size',
            'file_content',
            'created_at']
        

def validate_file_size(file):
    # print('validating size')
    min_size = 512  # 0.5 KB
    max_size = 2048  # 2 KB
    if file.size < min_size or file.size > max_size:
        raise serializers.ValidationError(f"File size must be between {min_size / 1024} KB and {max_size / 1024} KB.")

def validate_file_type(file):
    # print('validating type')
    if not file.content_type.startswith('text/plain'):
        raise serializers.ValidationError(f'File is not a valid plain text file.')
    
    # using mimetype
    mime_type, _ = guess_type(file.name)
    if mime_type != 'text/plain' and not file.name.lower().endswith('.txt'): # lower used here in case extension is .TXT which is valid
        raise serializers.ValidationError(f'File is not a valid plain text file.')
    
def check_file_name(filename, user):
    # check if the file_name exists
    base, ext = os.path.splitext(filename)
    counter = 1
    while TxtFile.objects.filter(file_name=filename).exists():
        filename = f"{base} ({counter}){ext}"
        counter += 1
    return filename

class TxtFileCreateSerializer(serializers.ModelSerializer):
    files = serializers.ListField(
        child=serializers.FileField(
            max_length=2048,
            allow_empty_file=False,
            use_url=False,
        )
    )

    class Meta:
        model = TxtFile
        fields = ['files']

    def validate(self, attrs):
        files = attrs.get("files")
        valid_files = []
        invalid_files = []

        for file in files:
            try:
                validate_file_type(file)
                validate_file_size(file)
                # Validate and read file
                file_data = {
                    "file": file,
                    "file_size": file.size,
                    "file_name": file.name,
                    "file_content": file.read().decode("utf-8"),  # Decoding validates for plain text
                }
                valid_files.append(file_data)
            except (UnicodeDecodeError, serializers.ValidationError) as e:
                # Collect invalid files with error details
                invalid_files.append({
                    "file_name": file.name,
                    "error": str(e),
                })

        # Store results in the serializer context for use in `save`
        self.context['valid_files'] = valid_files
        self.context['invalid_files'] = invalid_files

        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        valid_files = self.context.get('valid_files', [])
        invalid_files = self.context.get('invalid_files', [])
        saved_instances = []

        for file_data in valid_files:
            try:
                # Create and save a new TxtFile instance
                f_instance = TxtFile()
                f_instance.file_size = file_data["file_size"]
                f_instance.file_content = file_data["file_content"]

                # Check and save file name
                file_name = check_file_name(file_data["file_name"], user)
                f_instance.file_name = file_name
                
                save_dir_path = os.path.join('uploads', user.username or "Anon", file_name)
                file_fullname = default_storage.save(save_dir_path, file_data["file"])

                file_path = default_storage.url(file_fullname)
                file_path = "uploads" + file_path.split("uploads")[-1]
                f_instance.file_path = file_path

                f_instance.save()
                saved_instances.append(f_instance)

            except Exception as e:
                # Handle unexpected save errors
                invalid_files.append({
                    "file_name": file_data["file_name"],
                    "error": f"Failed to save: {str(e)}",
                })

        # Return results
        return {
            "saved_files": TxtFileSerializer(saved_instances, many=True).data,
            "invalid_files": invalid_files,
        }


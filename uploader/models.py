from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime
from uuid import uuid4

User = get_user_model()

def get_uuid():
    return uuid4().hex

# Create your models here.
class TxtFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file_name = models.CharField(max_length=255, db_index=True)
    file_content = models.TextField(db_index=True)
    uuid = models.CharField(max_length=64, default=get_uuid, unique=True, db_index=True)
    file_size = models.IntegerField()
    file_path = models.FilePathField(unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name
    
    def serialize(self):
        return {
            "uuid": self.uuid,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "created_at": datetime.strftime(self.created_at, "%d/%m/%Y, %H:%M:%S")
        }
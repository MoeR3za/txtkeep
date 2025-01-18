from django.urls import path
from uploader.views import FilesView, FileDetailView, FileDownloadView

urlpatterns = [
    path("files/", FilesView.as_view(), name='upload_file'),
    path("files/<str:uuid>/", FileDetailView.as_view(), name='file_details'),
    path("files/<str:uuid>/download/", FileDownloadView.as_view(), name='download_file'),
]
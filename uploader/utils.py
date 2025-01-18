import boto3

def download_file_from_s3(file_path, save_path, bucket_name='txtkeep', ):
    try:
        # Initialize the S3 client
        s3 = boto3.client('s3')
        
        # Download the file
        s3.download_file(bucket_name, file_path, save_path)
        print(f"File downloaded successfully: {save_path}")
    except Exception as e:
        print(f"Error downloading file from S3: {e}")

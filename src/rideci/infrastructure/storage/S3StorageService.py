import os
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, BotoCoreError
from src.rideci.core.settings import settings
from src.rideci.core.logging import logger

class S3StorageService:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name=os.getenv("AWS_REGION", "us-east-2"),
            config=Config(signature_version='s3v4')
        )
        self.bucket = settings.AWS_BUCKET_NAME

    def upload_file(self, file_content, file_name: str):
        try:
            self.s3.put_object(Bucket=self.bucket, Key=file_name, Body=file_content)
            return self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': file_name},
                ExpiresIn=3600
            )
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Error en S3: {str(e)}")
            raise RuntimeError("No se pudo persistir el archivo en la nube")
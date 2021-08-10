import boto3, random, os, string

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage


class TempStorageHelper:
  """
    A utility for uploading files to S3 and generating download URLs for them.
    In development environment, mocks S3 storage with local file storage.
  """
  DEFAULT_EXPIRATION = 36000  # 10 hours.

  def __init__(self, *args, **kwargs):
    if settings.AWS_ACCESS_KEY_ID:
      # True S3 access.
      kwargs['bucket'] = settings.TEMP_BUCKET_NAME
      self.storage = S3Boto3Storage(*args, **kwargs)
      self.bucket_name = bucket_name
      self.s3_client = boto3.client('s3',
                                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    else:
      # Mocked S3 access.
      self.storage = FileSystemStorage()
      self.s3_client = None

  def save_content(self, path, content, **kwargs):
    """
      Copy the given binary content to the S3 bucket and assign it the given key.
    """
    return self.storage.save(path, ContentFile(content))

  def generate_download_url(self, s3_key, **kwargs):
    """
      Generate a signed URL that may be used temporarily to download the S3
      object at the given key.
    """
    if self.s3_client:
      expiration = kwargs.get("expiration", self.DEFAULT_EXPIRATION)
      return self.s3_client.generate_presigned_url('get_object',
                                                   Params={
                                                       "Bucket": self.bucket_name,
                                                       "Key": s3_key
                                                   },
                                                   ExpiresIn=expiration)
    else:
      return f"{settings.SITE_URL}{settings.MEDIA_URL}{s3_key}"  # dev mode

  def save_content_for_download(self, content, **kwargs):
    """
      Copy the given binary content to the S3 bucket and assign it the given key.
      Return a signed URL that may be used temporarily to download the S3 object.
    """
    path = "".join(random.choice(string.ascii_letters + string.digits) for i in range(16))
    s3_key = self.save_content(path, content, **kwargs)
    return self.generate_download_url(s3_key, **kwargs)

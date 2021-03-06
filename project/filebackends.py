from storages.backends.s3boto3 import S3Boto3Storage

# not allow overwrite of same file
#aa
class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False

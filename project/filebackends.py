from storages.backends.s3boto3 import S3Boto3Storage


# not allow overwrite of same file
class MediaStorage(S3Boto3Storage):
    location = "media"
    file_overwrite = False

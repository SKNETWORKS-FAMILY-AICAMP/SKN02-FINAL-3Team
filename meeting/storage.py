import boto3

class S3Client():
    def __init__(self, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id = AWS_ACCESS_KEY_ID,
            aws_secret_access_key = AWS_SECRET_ACCESS_KEY
        )
        self.base = 'record/'

    def __del__(self):
        return None

    def upload(self, file, file_name, bucket_name):
        self.s3.upload_fileobj(
            file,
            bucket_name,
            self.base + file_name,
            ExtraArgs = {
                'ContentType': file.content_type
            }
        )

    def delete(self, file_name, bucket_name):
        self.s3.delete_object(Bucket=bucket_name, Key=self.base + file_name)
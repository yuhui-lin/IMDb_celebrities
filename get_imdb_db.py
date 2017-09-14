import boto3
import botocore

BUCKET_NAME = 'imdb-datasets' # replace with your bucket name
FILE_NAMES = ['title.crew.tsv.gz', 'title.episode.tsv.gz',
              'title.principals.tsv.gz', 'title.ratings.tsv.gz',
              'name.basics.tsv.gz', 'title.basics.tsv.gz']
KEY = 'documents/v1/current/{}'

s3 = boto3.resource('s3')

try:
    # s3.meta.client.download_file(BUCKET_NAME, KEY, FILE_NAME, {'RequestPayer':'requester'})

    bucket = s3.Bucket(BUCKET_NAME)
    for file_name in FILE_NAMES:
        bucket.download_file(KEY.format(file_name), file_name,
                             {'RequestPayer':'requester'})

    # bucket_request_payment = s3.BucketRequestPayment(BUCKET_NAME)
    # print(bucket_request_payment.payer)
    # bucket_request_payment.put(
    #     RequestPaymentConfiguration={
    #         'Payer': 'Requester'
    #     }
    # )
    # print(bucket_request_payment.payer)
    # # bucket_request_payment.payer = 'requester'
    # bucket_request_payment.load()
    # bucket = bucket_request_payment.Bucket()
    # for object in bucket.objects.all():
    #     print(object)
except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
        print("The object does not exist.")
    else:
        raise

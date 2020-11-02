import boto3
import json

BUCKET_NAME = 'natarova'

def s3_client():
    s3 = boto3.client('s3')
    return s3

def create_bucket(bucket_name):
    return s3_client().create_bucket(
        Bucket = bucket_name,
        CreateBucketConfiguration = {
            'LocationConstraint': 'eu-central-1',
        }
    )

def create_bucket_policy():
    bucket_policy = {
        'Version': '2012-10-17',
        'Statement': [
            {
                'Sid': 'AddPerm',
                'Effect': 'Allow',
                'Principal': '*',
                'Action': ['s3:*'],
                'Resource': ['arn:aws:s3:::natarova/*'],
            }
        ]
    }
    policy_string = json.dumps(bucket_policy)

    return s3_client().put_bucket_policy(
        Bucket = BUCKET_NAME,
        Policy = policy_string,
    )

def list_buckets():
    return s3_client().list_buckets()

def get_bucket_policy():
    return s3_client().get_bucket_policy(Bucket=BUCKET_NAME)

def get_bucket_encryption():
    return s3_client.get_bucket_encruption(Bucket=BUCKET_NAME)

def update_bucket_policy(bucket_name):
    bucket_policy = {
        'Version': '2012-10-17',
        'Statement': [
            {
                'Sid': 'AddPerm',
                'Effect': 'Allow',
                'Principal': '*',
                'Action': [
                    's3:DeleteObject',
                    's3:GetObject',
                    's3:PutObject',
                ],
                'Resource': [r'arn:aws:s3:::natarova/*'],
            }
        ]
    }

def server_side_encrypt_bucket():
    return s3_client().put_bucket_encryption(
        Bucket = BUCKET_NAME,
        ServerSideEncryptionConfiguration = {
            'Rules': [
                {
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    }
                }
            ]
        }
    )

def delete_bucket():
    return s3_client().delete_bucket(Bucket=BUCKET_NAME)

if __name__=='__main__':
    # print(create_bucket(BUCKET_NAME))
    # print(create_bucket_policy())
    # print( list_buckets() )
    print(get_bucket_policy())
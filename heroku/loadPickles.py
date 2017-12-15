# loadPickles.py
#
# This file loads the raw pickle files from the Amazon S3 bucket.

import boto3
import botocore
import os.path

BUCKET_NAME = 'acronym-classifier-weights' 

s3 = boto3.resource('s3')

filenames = ['naivebayes.pkl', 'vectorizer.pkl']

for filename in filenames:
    if (not os.path.isfile('trained-models/' + filename)):
        try:
            s3.Bucket(BUCKET_NAME).download_file(filename, 'trained-models/' + filename)
    
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print(filename + " does not exist.")
            else:
                raise
            
            

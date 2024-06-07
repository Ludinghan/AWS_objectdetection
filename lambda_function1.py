'''

Aim: This is the code for the Lamda function used in AWS.
This function is to retrive the image uploaded to the S3 storage and
use the image objectDectection.py to detect the object in it,
then write the output to Dynamo DB.

'''

import cv2
import numpy as np
from PIL import Image
import io
import boto3
import objectDetection as od
import uuid
import base64
from urllib.parse import unquote_plus
import json

# Define the Lambda handler function to process the event triggered by S3.
def lambda_handler(event, context):
    # Initialize the S3 client.
    s3 = boto3.client('s3')

    # Process each record in the event. Typically, these are triggered by uploads to S3.
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        download_path = f'/tmp/{key}'
        print("File {0} uploaded to {1} bucket".format(key, bucket))

        # Retrieve the object from S3.
        objectFile = s3.get_object(Bucket=bucket, Key=key)
        url = f'https://{bucket}.s3.amazonaws.com/{key}'

        # Read the content of the image file from the S3 object.
        image_file = objectFile['Body'].read()
        print(image_file)

        # Perform object detection on the image.
        output = od.objectDetect(image_file)
        print(output)

        # Download the image to a temporary path on the Lambda environment.
        s3.download_file(Bucket=bucket, Key=key, Filename=download_path)

        # Open the downloaded image and convert it to a NumPy array.
        image = Image.open(download_path)
        image_np = np.array(image)

        # Calculate the scaling factor to resize the image, maintaining the aspect ratio.
        max_dimension = 100
        height, width = image_np.shape[:2]
        scaling_factor = min(max_dimension / width, max_dimension / height)

        # Resize the image using the calculated scaling factor.
        resized_image = cv2.resize(image_np, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)

        # Save the resized image to a temporary path and upload it to a different S3 bucket.
        output_path = f'/tmp/resized-{key}'
        cv2.imwrite(output_path, resized_image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

        new_bucket = 'thumbnail-ldh'
        s3.upload_file(Filename=output_path, Bucket=new_bucket, Key=f'resized/{key}')
        url_resize = f'https://{new_bucket}.s3.amazonaws.com/resized/{key}'

        # Initialize DynamoDB client.
        dynamodb = boto3.client('dynamodb')
        TABLE_NAME = 'detectedImage'

        # Check if the object detection yielded results.
        if len(output) > 0:
            tmp = []
            for detectedObject in output:
                # Simplified for clarity: only save the label of each detected object.
                item1 = {"S": str(detectedObject[0])}
                tmp.append(item1)
            print(tmp)
            item2 = {
                "url": {"S": url},
                "tag": {"L": tmp},
                "url_resize": {"S": url_resize}
            }

            # Write the detection results along with the original and resized image URLs to DynamoDB.
            dynamodb.put_item(TableName=TABLE_NAME, Item=item2)

            return {
                'statusCode': 200,
                'body': json.dumps('Images detection data successfully inserted into database...')
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps('No object detected...')
            }




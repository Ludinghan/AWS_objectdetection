"""
Aim: This is the lamdba function to delete the image.
It get the image to be deleted from the URL sent in the POST body,
then it removed the images received from DynamoDB and S3 bucket.

"""

import boto3
from botocore.exceptions import ClientError
import json
import decimal

# Helper class to convert a DynamoDB item to JSON.
# This custom JSONEncoder class handles decimal.Decimal instances and sets, which are common in DynamoDB.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            # Convert decimal instances to strings to avoid JSON serialization issues.
            return str(o)
        if isinstance(o, set):
            # Convert sets to lists as JSON does not support 'set' datatype.
            return list(o)
        # Use the default method for other types.
        return super(DecimalEncoder, self).default(o)

# Lambda handler function to process the event and context.
def delete_handler(event, context):
    # Extract URL from the event object, which is provided by API Gateway.
    theurl = event['body-json']['url']

    # Initialize DynamoDB resource.
    client = boto3.resource("dynamodb")
    # Access the DynamoDB table where the images are referenced.
    table = client.Table("detectedImage")

    # Initialize the S3 resource.
    s3 = boto3.resource('s3')
    # Specify the S3 bucket name.
    bucket = "object-detection-tagging"

    print("Attempting a delete...")

    try:
        # Delete the item from the DynamoDB table based on the provided URL.
        response = table.delete_item(
            Key={
                'url': theurl
            }
        )
        print("The URL received:", theurl)
        # Extract the key part from the URL to use as the S3 object key.
        print("Extracted key:", theurl[50:])  # Assumes the key starts at character 50, which is specific to this URL format.
        # Retrieve the object from S3 using the extracted key and delete it.
        obj = s3.Object(bucket, theurl[50:])
        obj.delete()
        print("delete successfully")

    except ClientError as e:
        # Handle client errors from AWS services.
        print(e)
        # Return an error response, suitable for API Gateway integration.
        retrun_items = {"error": e}
        return retrun_items

    else:
        # Return a successful response if no exceptions were raised.
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": "Delete Complete!"
        }


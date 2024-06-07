"""
Aim: This is the function to find the images by specifying the tag of the image from dynamodb


"""

import boto3
from botocore.exceptions import ClientError
import json
import decimal  # Ensure decimal is imported for handling DynamoDB decimals

# Helper class to handle JSON serialization of DynamoDB items.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        # Convert DynamoDB decimals to string to prevent JSON serialization errors.
        if isinstance(o, decimal.Decimal):
            return str(o)
        # Convert sets to lists, because JSON does not support 'set' datatype.
        if isinstance(o, set):
            return list(o)
        # Use the default serialization for other types.
        return super(DecimalEncoder, self).default(o)

# Lambda function handler to process events and context from AWS Lambda.
def get_handler(event, context):
    # Extract labels (tags) from the event body passed by API Gateway.
    labels = event['body-json']['tags']
    print(labels)  # Debugging to check received labels.

    # Initialize DynamoDB resource.
    client = boto3.resource("dynamodb")
    # Access the specific DynamoDB table.
    table = client.Table("detectedImage")

    # Scan the table and retrieve all items.
    items = table.scan()['Items']

    scanned_images = []  # List to store URLs of images that match the labels.
    try:
        # Remove duplicates in labels for efficient comparison.
        labels = list(set(labels))

        # Iterate over all items retrieved from DynamoDB.
        for i in items:
            tags = i['tag']  # Each item's tags.
            print(tags)  # Debugging to check tags of each item.

            # Flag to check if all labels are present in tags.
            flag = True
            for l in labels:
                if l not in tags:
                    flag = False

            # If all labels match the tags, append the image URL to the list.
            if flag == True:
                scanned_images.append(i['url'])
                print(scanned_images)  # Debugging to check matched image URLs.

        # Prepare the return dictionary with matched image URLs.
        retrun_items = {"links": scanned_images}

    except ClientError as e:
        # Handle exceptions from AWS services.
        print(e)
        # Return an error message if an exception occurs.
        return {
            "isBase64Encoded": False,
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(e)
        }

    else:
        # If no exceptions, return the list of matched image URLs.
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(retrun_items)
        }

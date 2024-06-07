"""
Aim: This is the  function to out a new tag to the image in dynamodb


"""

import boto3
from botocore.exceptions import ClientError
import json
import decimal  # Ensure to import the decimal module for handling DynamoDB decimal types.

# Custom JSON encoder to handle DynamoDB data types
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        # Convert DynamoDB decimal to string to prevent serialization issues.
        if isinstance(o, decimal.Decimal):
            return str(o)
        # Convert sets to lists as JSON does not support 'set' datatype.
        if isinstance(o, set):
            return list(o)
        return super(DecimalEncoder, self).default(o)

# Function to handle PUT requests for updating image tags in DynamoDB.
def put_handler(event, context):
    # Extract tags and URL from the event body.
    labels = event['body-json']['tags']
    theurl = event['body-json']['url']

    # Initialize DynamoDB resource.
    client = boto3.resource("dynamodb")
    table = client.Table("detectedImage")

    try:
        # Retrieve existing tags for the given URL from DynamoDB.
        print("Retrieving original tags...")
        item = table.get_item(Key={'url': theurl})
        tags = item['Item']['tag']

        # Concatenate new tags to existing tags.
        concatenateList = tags + labels
        print(tags)
        print(concatenateList)
        print("Attempting a tag update...")

        # Update the 'tag' attribute of the item with new concatenated list of tags.
        response = table.update_item(
            Key={'url': theurl},
            UpdateExpression="set tag =:t",
            ExpressionAttributeValues={':t': concatenateList},
            ReturnValues="UPDATED_NEW"
        )

    except ClientError as e:
        # Handle client errors from AWS services.
        print(e)
        # Return an error response if there is an issue with DynamoDB operations.
        return_items = {"error": e}
        return return_items

    else:
        # Return a success response indicating completion of tag insertion.
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": "Insertion Complete!"
        }


import findimagesbytags as fit
import deleteimages as di
import putnewtags as pnt

"""
Aim: This is the lamda function to check the request method.
If the request method is DELETE, it will use the deleteimage.py
If the request method is PUT, it will use the putnewtags.py
If the request method is POST, it will use the findimagesbytags.py

"""


# Define the Lambda function handler to process HTTP requests.
def lambda_handler(event, context):
    # Extract the HTTP method from the event object provided by API Gateway.
    theRequest = event['http-method']

    # Check the type of HTTP request and call the corresponding function.
    if theRequest == 'DELETE':
        # Handle DELETE requests.
        print("DELETE request")
        returnItem = di.delete_handler(event, context)  # Call the delete handler function from the 'di' module.

    elif theRequest == 'PUT':
        # Handle PUT requests.
        print("PUT request")
        returnItem = pnt.put_handler(event, context)  # Call the put handler function from the 'pnt' module.

    elif theRequest == 'POST':
        # Handle POST requests.
        print("POST request")
        returnItem = fit.get_handler(event, context)  # Call the post handler function from the 'fit' module.

    # Example for additional or temporarily changed POST request handling.
    # Uncomment the below section if testing or handling a different type of POST request.
    # elif (theRequest == 'POST'):  # Temporarily changed handling for another type of POST request.
    #     print("this is post")
    #     returnItem = testpost.get_handler(event, context)  # Call an alternative post handler function from the 'testpost' module.
    #
    #     # The following commented-out code represents a typical sequence where:
    #     # - An image is parsed from the front end.
    #     # - The image is then processed by an object detection function.
    #     # image_file = None  # Placeholder to obtain the image data.
    #     # output = od.objectDetect(image_file)  # Call object detection function from the 'od' module with the image.
    #     # print(output)  # Print the output from the object detection.

    # Return the result from the handler function.
    return returnItem

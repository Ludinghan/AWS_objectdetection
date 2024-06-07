"""
Author: Lu Dinghan
Aim: This is a Python file to detect the object in image using Yolo library and OpenCV,
and generate the output in JSON format.

"""

import numpy as np
import sys
import time
import cv2
import os
import uuid
import base64
import json

# Set thresholds for filtering weak detections
confthres = 0.3  # Confidence threshold
nmsthres = 0.1   # Non-maximum suppression threshold

def get_labels(labels_path):
    # Read the labels from a file and return them as a list
    LABELS = open(labels_path).read().strip().split("\n")
    return LABELS

def get_weights(weights_path):
    # Return the path to the YOLO weights file
    return weights_path

def get_config(config_path):
    # Return the path to the YOLO configuration file
    return config_path

def load_model(configpath, weightspath):
    # Load the YOLO model from the configuration and weights file
    print("[INFO] loading YOLO from disk...")
    net = cv2.dnn.readNetFromDarknet(configpath, weightspath)
    return net

def do_prediction(image, net, LABELS):
    # Perform object detection on an image using the loaded YOLO model
    (H, W) = image.shape[:2]
    print(H, W)

    # Get the names of the output layers
    ln = net.getLayerNames()
    print(ln)
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    print(ln)

    # Create a blob from the image to feed to the neural network
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    print("[INFO] loading 2")
    net.setInput(blob)
    print("[INFO] loading 3")
    start = time.time()
    layerOutputs = net.forward(ln)
    end = time.time()
    print("[INFO] YOLO took {:.6f} seconds".format(end - start))

    # Initialize lists to hold detection bounding boxes, confidences, and class IDs
    boxes = []
    confidences = []
    classIDs = []

    # Process each output layer
    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]  # Extract the scores (class probabilities)
            classID = np.argmax(scores)
            confidence = scores[classID]

            if confidence > confthres:
                # Scale the bounding box coordinates back relative to the size of the image
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    # Apply non-maxima suppression to suppress weak, overlapping bounding boxes
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, confthres, nmsthres)

    # Compile the final output list
    output = []
    if len(idxs) > 0:
        for i in idxs.flatten():
            output.append([LABELS[classIDs[i]], confidences[i], boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]])
            print("Detected item: {}, Accuracy: {}, X: {}, Y: {}, Width: {}, Height: {}".format(
                LABELS[classIDs[i]], confidences[i], boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]))

    return output

def objectDetect(image_file):
    # Define paths to the YOLO configuration and weights
    labelsPath = "/opt/yolo_tiny_configs/coco.names"
    cfgpath = "/opt/yolo_tiny_configs/yolov3-tiny.cfg"
    wpath = "/opt/yolo_tiny_configs/yolov3-tiny.weights"

    # Load labels and model configuration
    Labels = get_labels(labelsPath)
    CFG = get_config(cfgpath)
    Weights = get_weights(wpath)

    try:
        # Convert image from bytes to a NumPy array
        image_as_np = np.fromstring(image_file, dtype=np.uint8)
        img = cv2.imdecode(image_as_np, flags=1)
        image = img.copy()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Load and execute the model
        nets = load_model(CFG, Weights)
        print("[INFO] loading 1")
        output = do_prediction(image, nets, Labels)
        print("[INFO] do_prediction...")

    except Exception as e:
        print("Exception: {}".format(e))

    return output





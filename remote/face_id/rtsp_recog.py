# Import necessary modules and packages
import os
import cv2
import requests
import datetime
from options import Options
from imutils.video import VideoStream

# Create an instance of the Options class
opts = Options()

# Define function to recognize a face !!!
def recognize_face(img_path):
    # This function sends the image to the server to detect the faces in the image
    # and returns the user id(s) of the recognized face(s). !!!
    # Create an instance of the Options class
    opts = Options()

    # Build the file path to the image
    filepath = os.path.join(opts.imageDir, img_path)
    # Read the image data as bytes
    image_data = open(filepath, "rb").read()
    
    try:
        # Send the image to the server to recognize the face(s) !!!
        response = requests.post(opts.endpoint("vision/face/recognize"),
                                files={"image": image_data},
                                data={"min_confidence": 0.6}).json()
        return response
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


# Define the main function
def main():
    # Captures the video frames from the camera,
    # detects the faces in the frames,
    # and sends them to the server for recognition. !!!
    
    # Initialise capturing video from the default camera
    # 0 for default camera, 1 if you have installed third-party webcam apps
    #cap = VideoStream(0).start()
    cap = VideoStream('rtsp://100.70.118.250:8080/').start()

    # Initialize variables to keep track of frame count, predictions, and frame skipping
    frame_index = 0
    predictions = {}
    skip_frame = 5

    # Begin the main loop to process frames from the camera
    while True:

        # Check for the 'q' key to exit the program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Stop capturing...")
            break

        # Capture a frame from the camera
        frame = cap.read()
        if frame is None:
            print("Camera closed")
            break
        
        # Increment the frame count
        frame_index += 1

        # Skip some frames to reduce the processing load
        if skip_frame > 1:
            if frame_index % skip_frame != 0:
                continue

        # Get the current timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add the timestamp to the frame
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)

        # Encode the frame in JPEG format
        retval, new_frame = cv2.imencode('.jpg', frame)

        try:
            # Send the frame to the server to detect the face(s) in the frame
            response = requests.post(opts.endpoint("vision/face"),
                                    files={"image": new_frame}).json()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        # Extract the predictions from the response
        predictions = response.get('predictions', [])
        # Get the number of predictions (i.e. faces detected)
        num_prediction_json = len(predictions)

        # Loop over the predictions and draw a rectangle around each face in the frame
        if num_prediction_json == 1:
            for i in range(num_prediction_json):
                blue, green, red = 0, 0, 255
                frame = cv2.rectangle(frame,
                                      (predictions[i]['x_min'], predictions[i]['y_min']),
                                      (predictions[i]['x_max'], predictions[i]['y_max']),
                                      (blue, green, red), 2)
                # Save the frame as an image file named "image.jpg"
                cv2.imwrite('image.jpg', frame)

                # Get response
                result = recognize_face("image.jpg")

                # Check if any detected faces are recognized
                if "predictions" in result:
                    # Get userid
                    for user in result["predictions"]:
                        recognized_ID=user["userid"]
                        #Check if userid is None or unknown
                        if recognized_ID and recognized_ID != "unknown":
                            #Print out name of recognized face
                            print(f'Recognized as: {user["userid"]}')
                            # Add name right next to the rectangle
                            cv2.putText(frame, recognized_ID, (predictions[i]['x_min'], predictions[i]['y_min']-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                        else:
                            print("No face(s) recognized!!!")
        else:
            print('Make sure you are showing your face ONLY and CLEARLY...')

        cv2.imshow('Image Viewer', frame)

    # Release the camera and close all windows
    cap.stop()
    cv2.destroyAllWindows()


# Call the main function if this script is being run directly
if __name__ == "__main__":
    main()
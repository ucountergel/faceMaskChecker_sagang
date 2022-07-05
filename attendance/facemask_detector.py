import winsound
import cv2
import imutils
import numpy as np
import os
import urllib.request
from django.conf import settings
from django.shortcuts import render
from imutils.video import VideoStream
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
# from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing.image import img_to_array

'''face_detection_videocam = cv2.CascadeClassifier(os.path.join(
    settings.BASE_DIR, 'attendance/face_detector_model/opencv_haarcascade_data/haarcascade_frontalface_default.xml'))
face_detection_webcam = cv2.CascadeClassifier(os.path.join(
    settings.BASE_DIR, 'attendance/face_detector_model/opencv_haarcascade_data/haarcascade_frontalface_default.xml'))'''
# load our serialized face detector model from disk
prototxtPath = os.path.sep.join([settings.BASE_DIR, "attendance/face_detector_model/deploy.prototxt"])
weightsPath = os.path.sep.join(
    [settings.BASE_DIR, "attendance/face_detector_model/res10_300x300_ssd_iter_140000.caffemodel"])
faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)
maskNet = load_model(os.path.join(settings.BASE_DIR, 'attendance/mask_detector_model/maskmodel.h5'))
network = cv2.dnn.readNetFromCaffe("attendance/ssd/SSD_MobileNet_prototxt.txt",
                                   "attendance/ssd/SSD_MobileNet.caffemodel")


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces_detected = weightsPath.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        for (x, y, w, h) in faces_detected:
            cv2.rectangle(image, pt1=(x, y), pt2=(x + w, y + h), color=(255, 0, 0), thickness=2)
        # frame = imutils.resize(image, width=800)
        # (h, w) = frame.shape[:2]
        # frame_flip = cv2.flip(image, 1)

        frame_flip = cv2.flip(image, 1)
        ret, jpeg = cv2.imencode('.jpg', frame_flip)
        return jpeg.tobytes()


class IPWebCam(object):
    def __init__(self):
        self.url = "http://192.168.254.254:8080/shot.jpg"

    def __del__(self):
        cv2.destroyAllWindows()

    def get_frame(self):
        imgResp = urllib.request.urlopen(self.url)
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces_detected = weightsPath.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        for (x, y, w, h) in faces_detected:
            cv2.rectangle(img, pt1=(x, y), pt2=(x + w, y + h), color=(255, 0, 0), thickness=2)
        resize = cv2.resize(img, (640, 480), interpolation=cv2.INTER_LINEAR)
        frame_flip = cv2.flip(resize, 1)
        ret, jpeg = cv2.imencode('.jpg', frame_flip)
        return jpeg.tobytes()


class MaskDetect(object):
    def __init__(self):
        self.vs = VideoStream(src=0).start()

    # Define the codec and create VideoWriter object
    '''fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))'''

    def detect_and_predict_mask(self, frame, faceNet, maskNet):
        # grab the dimensions of the frame and then construct a blob
        # from it
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (224, 224), (104.0, 177.0, 123.0))

        # pass the blob through the network and obtain the face detections
        faceNet.setInput(blob)
        detections = faceNet.forward()
        # print(detections.shape)

        # initialize our list of faces, their corresponding locations,
        # and the list of predictions from our face mask network
        faces = []
        locs = []
        preds = []

        # loop over the detections
        for i in range(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the detection
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the confidence is
            # greater than the minimum confidence
            if confidence > 0.4:
                # compute the (x, y)-coordinates of the bounding box for the object
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # ensure the bounding boxes fall within the dimensions of the frame
                (startX, startY) = (max(0, startX), max(0, startY))
                (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

                # extract the face ROI, convert it from BGR to RGB channel
                # ordering, resize it to 224x224, and preprocess it
                face = frame[startY:endY, startX:endX]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                face = cv2.resize(face, (224, 224))
                face = img_to_array(face)
                face = preprocess_input(face)

                # add the face and bounding boxes to their respective lists
                faces.append(face)
                locs.append((startX, startY, endX, endY))

        # only make a predictions if at least one face was detected
        if len(faces) > 0:
            # for faster inference we'll make batch predictions on *all*
            # faces at the same time rather than one-by-one predictions
            # in the above `for` loop
            faces = np.array(faces, dtype="float32")
            preds = maskNet.predict(faces, batch_size=32)

        # return a 2-tuple of the face locations and their corresponding locations
        return locs, preds

    def get_frame(self):

        # global statusLabel
        labels = [line.strip() for line in
                  open("class_labels.txt")]
        # Generate random bounding box bounding_box_color for each label
        bounding_box_color = np.random.uniform(0, 255, size=(len(labels), 3))

        frame = self.vs.read()
        frame = imutils.resize(frame, width=800)
        (h, w) = frame.shape[:2]

        # Resize the frame to suite the model requirements. Resize the frame to 300X300 pixels
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

        (locs, preds) = self.detect_and_predict_mask(frame, faceNet, maskNet)
        network.setInput(blob)
        detections = network.forward()

        pos_dict = dict()
        coordinates = dict()
        counts = 1
        maskCount = 0
        improperCount = 0
        withoutMaskCount = 0
        statusLabel = ''

        for (box, pred) in zip(locs, preds):
            # unpack the bounding box and predictions
            (startX, startY, endX, endY) = box
            (mask, withoutMask, improper) = pred

            # removed nums = len(locs)
            # initialize count of 3 datasets, improper and no face masks are violations

            # determine the class label and color we'll use to draw the bounding box and text
            # include the probability in the label
            if mask > withoutMask and mask > improper:
                label = "With Face Mask"
                color = (0, 255, 0)
                maskCount += 1
                statusLabel = "Safe-"

            elif withoutMask > mask and withoutMask > improper:
                label = "Improper Face Mask"
                color = (255, 0, 0)
                # Alarm when wearing 'Improper Face Mask'
                '''winsound.PlaySound(
                      'attendance/static/assets/alarm/beep.wav',
                    winsound.SND_ASYNC)'''
                improperCount += 1
                statusLabel = "Warning-"

            else:
                label = "No Face Mask"
                color = (0, 0, 255)
                withoutMaskCount += 1
                # Alarm when 'Not Wearing Face Mask'
                winsound.PlaySound(
                     'attendance/static/assets/alarm/beep.wav',
                    winsound.SND_ASYNC)
                statusLabel = "Danger-"

            # print(label)
            label = "{}{}: {:.2f}%".format(statusLabel, label, max(mask, withoutMask, improper) * 100)
            # display the label and bounding box rectangle on the output
            cv2.putText(frame, label, (startX, startY - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.70, color, 2)
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

            counts += 1
        cv2.putText(frame, f'Number of Faces: {counts - 1} detected', (420, 40),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 0), 2)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()



class MaskDetects(object):
    def __init__(self):
        self.vs = VideoStream(src=0).stop()


class LiveWebCam(object):
    def __init__(self):
        self.url = cv2.VideoCapture("rtsp://192.168.254.254:8080/out.h264/")

    def __del__(self):
        cv2.destroyAllWindows()

    def get_frame(self):
        success, imgNp = self.url.read()
        resize = cv2.resize(imgNp, (640, 480), interpolation=cv2.INTER_LINEAR)
        ret, jpeg = cv2.imencode('.jpg', resize)
        return jpeg.tobytes()

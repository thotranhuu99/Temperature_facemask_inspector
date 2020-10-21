from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import concurrent.futures
import imutils
import cv2
import os
from Cam_lib.Stream_lib import Picam_lib
import socket


class LeptonThreadClass:
    Server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    Client_address = ["", int()]
    Server_address = ("127.0.0.1", 6000)

    Received_data = bytearray()
    Serialized_bytes_received = np.zeros(4800)
    Img_received = np.zeros([60, 80], dtype=np.uint16)
    Calculated_temp_img = np.ones([60, 80], dtype=np.uint16)

    def receive(self):
        try:
            self.Received_data, self.Client_address = self.Server_sock.recvfrom(10240)
            self.Serialized_bytes_received = np.frombuffer(self.Received_data, dtype=np.uint16)
            self.Img_received = np.reshape(self.Serialized_bytes_received, newshape=(60, 80))
        except Exception:
            return self.Calculated_temp_img
        self.Calculated_temp_img = default_temp(self.Img_received.astype(float))
        return self.Calculated_temp_img


class CameraParams:
    lepton_left_top = (16, 46)
    lepton_right_bot = (326, 280)


def default_temp(pixel_value):
    temperature = pixel_value / 100 - 273.3
    return temperature


def run_model():
    """Initialize Connection"""
    lepton_thread = LeptonThreadClass()
    lepton_thread.Server_sock.bind(LeptonThreadClass.Server_address)
    lepton_thread.Server_sock.setblocking(False)
    """Initialize Connection"""

    """Start of initialize model"""
    print("[INFO] loading face detector model...")
    prototxt_path = os.path.sep.join(["Cam_lib", "Detection_lib", "deploy.prototxt"])
    weights_path = os.path.sep.join(["Cam_lib", "Detection_lib", "res10_300x300_ssd_iter_140000.caffemodel"])
    face_net = cv2.dnn.readNet(prototxt_path, weights_path)
    print("[INFO] loading face mask detector model...")
    mask_net = load_model("Cam_lib/Detection_lib/mask_detector.model")
    print("[INFO] starting video stream...")
    """End of initialize model"""
    while True:
        # start = time.time()
        lepton_frame = lepton_thread.receive()
        # stop = time.time()
        # print(lepton_frame)
        if np.max(lepton_frame) > np.min(lepton_frame):
            lepton_frame_norm = (lepton_frame - np.min(lepton_frame))/(np.max(lepton_frame) - np.min(lepton_frame)) \
                                * 255
        else:
            lepton_frame_norm = lepton_frame
        lepton_frame_norm = lepton_frame_norm.astype(np.uint8)
        lepton_frame_norm = cv2.resize(lepton_frame_norm, (800, 600), interpolation=cv2.INTER_AREA)
        lepton_frame_norm_colored = cv2.applyColorMap(lepton_frame_norm, cv2.COLORMAP_INFERNO)
        # print("Lepton: {}".format(lepton_frame_norm.shape))
        frame = cv2.imread("/mnt/ramdisk/out.bmp")
        frame = cv2.flip(frame, 0)
        try:
            frame = imutils.resize(frame, width=400)
            # print("Camera: {}".format(frame.shape))
            (locs, preds) = detect_and_predict_mask(frame, face_net, mask_net)
            for (box, pred) in zip(locs, preds):
                # unpack the bounding box and predictions
                (startX, startY, endX, endY) = box
                (mask, withoutMask) = pred

                # determine the class label and color we'll use to draw
                # the bounding box and text
                label = "Mask" if mask > withoutMask else "No Mask"
                color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

                # include the probability in the label
                label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

                # display the label and bounding box rectangle on the output
                # frame
                cv2.putText(frame, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
                cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

            # show the output frame
            cv2.rectangle(frame, CameraParams.lepton_left_top, CameraParams.lepton_right_bot, (255, 0, 0), 2)
            cv2.imshow("Camera frame", frame)
            cv2.imshow("Lepton frame", lepton_frame_norm_colored)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break
        except Exception:
            pass

    # do a bit of cleanup
    cv2.destroyAllWindows()


def detect_and_predict_mask(frame, facenet, masknet):
    # grab the dimensions of the frame and then construct a blob
    # from it
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300),
                                 (104.0, 177.0, 123.0))

    # pass the blob through the network and obtain the face detections
    facenet.setInput(blob)
    detections = facenet.forward()

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
        if confidence > 0.5:
            # compute the (x, y)-coordinates of the bounding box for
            # the object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # ensure the bounding boxes fall within the dimensions of
            # the frame
            (startX, startY) = (max(0, startX), max(0, startY))
            (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

            # extract the face ROI, convert it from BGR to RGB channel
            # ordering, resize it to 224x224, and preprocess it
            face = frame[startY:endY, startX:endX]
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            face = cv2.resize(face, (224, 224))
            face = img_to_array(face)
            face = preprocess_input(face)

            # add the face and bounding boxes to their respective
            # lists
            faces.append(face)
            locs.append((startX, startY, endX, endY))

    # only make a predictions if at least one face was detected
    if len(faces) > 0:
        # for faster inference we'll make batch predictions on *all*
        # faces at the same time rather than one-by-one predictions
        # in the above `for` loop
        faces = np.array(faces, dtype="float32")
        preds = masknet.predict(faces, batch_size=32)

    # return a 2-tuple of the face locations and their corresponding
    # locations
    return locs, preds


def rev_and_run_model():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        f1 = executor.submit(Picam_lib.read_fifo)
        f2 = executor.submit(run_model)


if __name__ == "__main__":
    rev_and_run_model()

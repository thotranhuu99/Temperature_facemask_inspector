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
import sys


class LeptonThreadClass:
    def __init__(self):
        self.Server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.Client_address = ["", int()]
        self.Server_address = ("127.0.0.1", 6000)

        self.Received_data = bytearray(10240)
        self.Serialized_bytes_received = np.zeros(4800)
        self.Img_received = np.zeros([60, 80], dtype=np.uint16)
        self.Calculated_temp_img = np.ones([60, 80], dtype=np.float)

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
    lepton_left_top_pixel = (16, 46)
    lepton_right_bot_pixel = (326, 280)


def default_temp(pixel_value):
    temperature = pixel_value / 100 - 273.3
    return temperature


def calc_lepton_coord(start_x_cam, start_y_cam, end_x_cam, end_y_cam):
    start_x_lep = max(0, ((start_x_cam - 16)/3.875 + 0.5).astype(np.int16))
    end_x_lep = min(79, ((end_x_cam - 16)/3.875 + 0.5).astype(np.int16))
    start_y_lep = max(0, ((start_y_cam - 46)/3.9 + 0.5).astype(np.int16))
    end_y_lep = min(79, ((end_y_cam - 46)/3.9 + 0.5).astype(np.int16))
    return start_x_lep, start_y_lep, end_x_lep, end_y_lep


def run_model():
    """Initialize Connection"""
    lepton_thread = LeptonThreadClass()
    lepton_thread.Server_sock.bind(lepton_thread.Server_address)
    lepton_thread.Server_sock.setblocking(False)
    """Initialize Connection"""

    """Start of initialize model"""
    print("[INFO] loading face detector model...")
    prototxt_path = os.path.sep.join(["Cam_lib", "Detection_lib", "deploy.prototxt"])
    weights_path = os.path.sep.join(["Cam_lib", "Detection_lib", "res10_300x300_ssd_iter_140000.caffemodel"])
    face_net = cv2.dnn.readNet(prototxt_path, weights_path)
    print("[INFO] loading face mask detector model...")
    mask_net = load_model("Cam_lib/Detection_lib/mask_detector_5k.model")
    print("[INFO] starting video stream...")
    """End of initialize model"""
    while True:
        lepton_frame = lepton_thread.receive()
        if np.max(lepton_frame) > np.min(lepton_frame):
            lepton_frame_norm = (lepton_frame - np.min(lepton_frame))/(np.max(lepton_frame) - np.min(lepton_frame)) \
                                * 255
        else:
            lepton_frame_norm = lepton_frame
        lepton_frame_norm = lepton_frame_norm.astype(np.uint8)
        # lepton_frame_norm_resized = cv2.resize(lepton_frame_norm, (800, 600), interpolation=cv2.INTER_AREA)
        # lepton_frame_norm_colored = cv2.applyColorMap(lepton_frame_norm_resized, cv2.COLORMAP_INFERNO)
        frame = cv2.imread("/mnt/ramdisk/out.bmp")
        frame = cv2.flip(frame, 0)
        if frame is not None:
            try:
                frame = imutils.resize(frame, width=400)
                # print("Camera: {}".format(frame.shape))
                (locs, preds) = detect_and_predict_mask(frame, face_net, mask_net)
                for (box_cam, pred_cam) in zip(locs, preds):
                    (startX_cam, startY_cam, endX_cam, endY_cam) = box_cam
                    (mask, withoutMask) = pred_cam
                    start_x_lept, start_y_lept, end_x_lept, end_y_lept = calc_lepton_coord(startX_cam, startY_cam,
                                                                                           endX_cam, endY_cam)
                    face_temp = lepton_frame[start_x_lept:(end_x_lept + 1), start_y_lept:(end_y_lept + 1)]
                    if face_temp.size != 0:
                        temperature = np.max(face_temp)
                        temp_text = "{:.2f} degree".format(temperature)
                        cv2.putText(frame, temp_text, (startX_cam - 20, endY_cam + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                                    (0, 215, 255), 1)
                    label = "Mask" if mask > withoutMask else "No Mask"
                    color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
                    label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)
                    cv2.putText(frame, label, (startX_cam, startY_cam - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
                    cv2.rectangle(frame, (startX_cam, startY_cam), (endX_cam, endY_cam), color, 2)
                    cv2.rectangle(lepton_frame_norm, (start_x_lept, start_y_lept), (end_x_lept, end_y_lept), 255, 1)
                cv2.rectangle(frame, CameraParams.lepton_left_top_pixel, CameraParams.lepton_right_bot_pixel, 255, 1)
                lepton_frame_norm_test = cv2.resize(lepton_frame_norm, (600, 450), interpolation=cv2.INTER_AREA)
                frame = cv2.resize(frame, (600, 450), interpolation=cv2.INTER_AREA)
                cv2.imshow("Camera frame", frame)
                cv2.imshow("Lepton frame", lepton_frame_norm_test)
                key = cv2.waitKey(1) & 0xFF

                # if the `q` key was pressed, break from the loop
                if key == ord("q"):
                    break
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, file_name, exc_tb.tb_lineno)
                print(e)

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

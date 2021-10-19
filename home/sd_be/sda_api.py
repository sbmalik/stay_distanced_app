import time
import urllib.request

import cv2
from home.sd_be.mylib import config, mailer
from home.sd_be.mylib.detection import detect_people
from scipy.spatial import distance as dist
import os
import imutils
import numpy as np
from home.models import Record, Place


class StreamingCamera(object):
    def __init__(self,
                 location=None):
        self.location = location
        api_path = os.path.join(os.getcwd(), 'home/sd_be')
        static_path = os.path.join(os.getcwd(), 'static/video')

        video_file_path = os.path.join(static_path, self.location.video_name)
        # video_file_path = os.path.join(api_path, 'mylib/videos/test.mp4')

        current_model = os.path.join(api_path, 'yolo')
        labelsPath = os.path.sep.join([current_model, "coco.names"])
        self.LABELS = open(labelsPath).read().strip().split("\n")

        # derive the paths to the YOLO weights and model configuration
        weightsPath = os.path.sep.join([current_model, "yolov3.weights"])
        configPath = os.path.sep.join([current_model, "yolov3.cfg"])
        # load our YOLO object detector trained on COCO dataset (80 classes)
        self.net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
        if config.USE_GPU:
            # set CUDA as the preferable backend and target
            print("")
            print("[INFO] Looking for GPU")
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

        # determine only the *output* layer names that we need from YOLO
        self.ln = self.net.getLayerNames()
        self.ln = [self.ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        if self.location.ip_url == '_':
            self.vs = cv2.VideoCapture(video_file_path)
        else:
            self.vs = None
        self.previous_time = time.time()
        # for Camera
        # self.vs = cv2.VideoCapture(0)

    def __del__(self):
        if self.vs:
            self.vs.release()
        cv2.destroyAllWindows()

    def get_frame(self):
        current_time = time.time()
        if self.vs:
            (grabbed, frame) = self.vs.read()
        else:
            img_res = urllib.request.urlopen(self.location.ip_url)
            img_np = np.array(bytearray(img_res.read()), dtype=np.uint8)
            frame = cv2.imdecode(img_np, 1)
        frame = imutils.resize(frame, width=700)
        n_people, results = detect_people(frame, self.net, self.ln,
                                          personIdx=self.LABELS.index("person"))
        # Setting the variables for the detection
        serious = set()
        abnormal = set()
        # ensure there are *at least* two people detections (required in
        # order to compute our pairwise distance maps)
        if len(results) >= 2:
            # extract all centroids from the results and compute the
            # Euclidean distances between all pairs of the centroids
            centroids = np.array([r[2] for r in results])
            D = dist.cdist(centroids, centroids, metric="euclidean")

            # loop over the upper triangular of the distance matrix
            for i in range(0, D.shape[0]):
                for j in range(i + 1, D.shape[1]):
                    # check to see if the distance between any two
                    # centroid pairs is less than the configured number of pixels
                    if D[i, j] < config.MIN_DISTANCE:
                        # update our violation set with the indexes of the centroid pairs
                        serious.add(i)
                        serious.add(j)
                    # update our abnormal set if the centroid distance is below max distance limit
                    if (D[i, j] < config.MAX_DISTANCE) and not serious:
                        abnormal.add(i)
                        abnormal.add(j)

        # loop over the results
        for (i, (prob, bbox, centroid)) in enumerate(results):
            # extract the bounding box and centroid coordinates, then
            # initialize the color of the annotation
            (startX, startY, endX, endY) = bbox
            (cX, cY) = centroid
            color = (0, 255, 0)

            # if the index pair exists within the violation/abnormal sets, then update the color
            if i in serious:
                color = (0, 0, 255)
            elif i in abnormal:
                color = (0, 255, 255)  # orange = (0, 165, 255)

            # draw (1) a bounding box around the person and (2) the
            # centroid coordinates of the person,
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
            cv2.circle(frame, (cX, cY), 5, color, 2)

        # draw some of the parameters
        Safe_Distance = "Safe distance: >{} px".format(config.MAX_DISTANCE)
        cv2.putText(frame, Safe_Distance, (470, frame.shape[0] - 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 0, 0), 2)
        Threshold = "Threshold limit: {}".format(config.Threshold)
        cv2.putText(frame, Threshold, (470, frame.shape[0] - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 0, 0), 2)

        # draw the total number of social distancing violations on the output frame
        text = "Total serious violations: {}".format(len(serious))
        cv2.putText(frame, text, (10, frame.shape[0] - 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.70, (0, 0, 255), 2)

        text1 = "Total abnormal violations: {}".format(len(abnormal))
        cv2.putText(frame, text1, (10, frame.shape[0] - 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.70, (0, 255, 255), 2)

        # ------------------------------Alert function----------------------------------#
        if len(serious) >= config.Threshold:
            # cv2.putText(frame, "-ALERT: Violations over limit-", (10, frame.shape[0] - 80),
            #             cv2.FONT_HERSHEY_COMPLEX, 0.60, (0, 0, 255), 2)
            if config.ALERT:
                Place.objects.filter(pk=self.location.id).update(is_alert=True)
                print("")
                print('[INFO] Sending mail...')
                mailer.Mailer().send(config.MAIL, self.location.location_name)
                print('[INFO] Mail sent')
                config.ALERT = False

        # TIMER
        if current_time - self.previous_time >= 6.0:
            print('6 seconds passed')
            Record.objects.create(
                location=self.location,
                total_people=n_people,
                total_violation=len(serious)
            )
            self.previous_time = current_time

        # Show to the web page
        # frame_flip = cv2.flip(frame, 1)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

import cv2
import datetime
import numpy as np
from keras.models import load_model
from keras.preprocessing import image
import os


class StreamingFaceMask(object):
    def __init__(self):
        api_path = os.path.join(os.getcwd(), 'home/sd_be_fm')
        self.mymodel = load_model(os.path.join(api_path, 'mymodel.h5'))
        self.face_cascade = cv2.CascadeClassifier(os.path.join(api_path, 'haarcascade_frontalface_default.xml'))
        self.cap = cv2.VideoCapture(0)

    def __del__(self):
        self.cap.release()

    def get_frame(self):
        (grabbed, frame) = self.cap.read()
        face = self.face_cascade.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=4)
        for (x, y, w, h) in face:
            face_img = frame[y:y + h, x:x + w]
            cv2.imwrite('temp.jpg', face_img)
            test_image = image.load_img('temp.jpg', target_size=(150, 150, 3))
            test_image = image.img_to_array(test_image)
            test_image = np.expand_dims(test_image, axis=0)
            pred = self.mymodel.predict(test_image)[0][0]
            # frame = cv2.flip(frame, 1)
            if pred == 1:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)
                cv2.putText(frame, 'NO MASK', ((x + w) // 2, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                cv2.putText(frame, 'MASK', ((x + w) // 2, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
            datet = str(datetime.datetime.now())
            cv2.putText(frame, datet, (400, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

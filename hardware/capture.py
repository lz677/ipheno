#!/usr/bin/env python
# encoding: utf-8

"""
@version: Python3.7
@author: Zhiyu YANG, Liu Zhe
@e-mail: zhiyu_yang@sjtu.edu.cn, LiuZhe_54677@sjtu.edu.cn
@file: capture.py
@time: 2020/5/5 14:40

Code is far away from bugs with the god animal protecting
"""
import cv2
import numpy as np
import time
import base64
import logging


class CaptureWebCam:
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture()
        self.will_quit = False
        self.save_img = False
        # self.cap = cv2.VideoCapture(0)

        self.img_stream = "NONE"
        _, self.blackJpeg = cv2.imencode('.jpg', np.zeros(shape=(480, 720), dtype=np.uint8))

        self.should_stream_stop = False

    def open(self, _id='/dev/video0'):
        self.cap.open(_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2880)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)
        self.cap.set(cv2.CAP_PROP_EXPOSURE, 0.001)

    def is_opened(self) -> bool:
        return self.cap.isOpened()

    def read(self) -> (bool, np.ndarray):
        return self.cap.read()

    def stop_stream(self):
        self.should_stream_stop = True

    def start_stream(self):
        self.should_stream_stop = False

    def gen_stream_web(self):
        while not self.will_quit:
            if self.cap.isOpened() and not self.should_stream_stop:
                # print('get stream')
                ret, frame = self.read()
                # if self.save_img:
                # cv2.imwrite('./static/1.jpg', frame)

                ret, jpeg = cv2.imencode('.jpg', frame)

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
            else:
                time.sleep(0.5)
            # else:
            #     yield (b'--frame\r\n'
            #            b'Content-Type: image/jpeg\r\n\r\n' + self.blackJpeg.tobytes() + b'\r\n\r\n')

    def gen_stream(self, is_jpg=True):
        if self.cap.isOpened() and not self.should_stream_stop:
            ret, frame = self.read()
            # frame = cv2.resize(frame, (200, 200))
            ret, img = cv2.imencode('.jpg', frame) if is_jpg else cv2.imencode('.png', frame)
            return img.tobytes()
        else:
            time.sleep(0.5)

    def get_img(self):
        if self.cap.isOpened():
            for i in range(5):
                ret, frame = self.read()
                if i == 4:
                    return frame
            # logging.warning('get get_img')

        else:
            time.sleep(0.5)

    def return_img_stream(self):
        while not self.will_quit:
            if self.cap.isOpened() and not self.should_stream_stop:
                ret, self.img_stream = self.read()
                # print(frame)
                ret, jpeg = cv2.imencode('.jpg', self.img_stream)
                img_stream = base64.b64encode(jpeg)
                img_stream = str(img_stream, 'utf8')
                return img_stream
                # yield (b'--frame\r\n'
                #        b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
            else:
                time.sleep(0.5)
        # frame = cv2.imread(img_local_path)
        # ret, jpeg = cv2.imencode('.jpg', frame)
        # # with open(img_local_path, 'rb') as img:
        # #     self.img_stream = img.read()
        # self.img_stream = base64.b64encode(jpeg)
        # self.img_stream = str(self.img_stream, 'utf8')
        # return self.img_stream

    def return_static_img(self):
        if self.img_stream == "NONE":
            return "NONE"
        else:
            ret, jpeg = cv2.imencode('.png', self.img_stream)
            img_stream = base64.b64encode(jpeg)
            img_stream = str(img_stream, 'utf8')
            return img_stream

    def release(self):
        self.will_quit = True
        self.cap.release()


if __name__ == '__main__':
    capture = CaptureWebCam()

#!/usr/bin/env python3

import time
start = time.time()
import argparse
import cv2
import os
import pickle
import sys
import numpy as np
np.set_printoptions(precision=2)
import dlib
detector = dlib.get_frontal_face_detector()
from sklearn.mixture import GMM
import openface
import pdb
import threading
import time
from websocket_server import WebsocketServer
# 识别的BoundingBox的框的大小，里边存储的就是检测到的人脸框
DETECTION_WIDTH = 480
DETECTION_HEIGHT = 270
# 人脸识别的名字
cam_dect_name = None
# 每一次的人脸识别的值
cam_confidences_count = 0
# 每三次识别进行一次去平均值
sum_cam_confidences = 0
cam_confidences = None
# 指定当前项目所在目录
fileDir = os.path.dirname(os.path.realpath(__file__))
# 指定Dlib以及OpenFace模块所在目录
modelDir = os.path.join(fileDir, '', 'models')
# 指定Dlib模块所在目录
dlibModelDir = os.path.join(modelDir, 'dlib')
# 指定OpenFace模块所在目录
openfaceModelDir = os.path.join(modelDir, 'openface')


def getRep(bgrImg):
    start = time.time()
    if bgrImg is None:
        raise Exception("Unable to load image/frame")
    # 对传入的图片进行颜色转换，转换成RGB格式的图片
    rgbImg = cv2.resize(
        cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB), (DETECTION_WIDTH, DETECTION_HEIGHT), interpolation=cv2.INTER_CUBIC)
    # 对传入的图片进行灰度图片提取
    gray = cv2.resize(
        cv2.cvtColor(bgrImg, cv2.COLOR_BGR2GRAY), (DETECTION_WIDTH, DETECTION_HEIGHT), interpolation=cv2.INTER_CUBIC)


    # 用Dlib的"get_frontal_face_detector()"函数进行人脸检测，传入的参数是刚才处理的灰度图片，并不对图片进行向下降采样
    bb = detector(gray, 0)

    if bb is None:
        return None

    start = time.time()

    alignedFaces = []
    for box in bb:
        alignedFaces.append(
            align.align(
                args.imgDim,
                rgbImg,
                box,
                landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE))

    if alignedFaces is None:
        raise Exception("Unable to align the frame")

    start = time.time()

    reps = []
    for alignedFace in alignedFaces:
        reps.append(net.forward(alignedFace))


    # print (reps)
    return (reps,bb)


def infer(img, args):
    with open(args.classifierModel, 'rb') as f:
        if sys.version_info[0] < 3:
                (le, clf) = pickle.load(f)  # le - label and clf - classifer
        else:
                #set_trace()
                (le, clf) = pickle.load(f, encoding='latin1')  # le - label and clf - classifer

    repsAndBBs = getRep(img)
    reps = repsAndBBs[0]
    bbs = repsAndBBs[1]
    persons = []
    confidences = []
    for rep in reps:
        try:
            rep = rep.reshape(1, -1)
        except:
            print ("No Face detected")
            return (None, None)
        start = time.time()
        predictions = clf.predict_proba(rep).ravel()
        # print (predictions)
        maxI = np.argmax(predictions)
        # max2 = np.argsort(predictions)[-3:][::-1][1]
        persons.append(le.inverse_transform(maxI))
        # print (str(le.inverse_transform(max2)) + ": "+str( predictions [max2]))
        # ^ prints the second prediction
        confidences.append(predictions[maxI])

        # print("Predict {} with {:.2f} confidence.".format(person.decode('utf-8'), confidence))
        if isinstance(clf, GMM):
            dist = np.linalg.norm(rep - clf.means_[maxI])
            print("  + Distance from the mean: {}".format(dist))
            pass
    return (persons, confidences ,bbs)

# 实现通过摄像头采集数据，并且进行人脸识别，同时通过管道技术，将摄像头拍到的图像同步传输到WEB服务端
def cam_dect():
    # cam_dect_name存放的是识别到的人的姓名
    global cam_dect_name
    # Capture device. Usually 0 will be webcam and 1 will be usb cam.
    # video_capture = cv2.VideoCapture(args.captureDevice)
    # video_capture.set(3, args.width)
    # video_capture.set(4, args.height)

    confidenceList = []

    # 通过管道技创建一个往里面写图片的文件，运用进程间管道通信技术
    invasion_subsys_name_pipe = "/tmp/IPC1_Image_Pipe"
    try:
        # os.unlink(invasion_subsys_name_pipe)
        os.mkfifo(invasion_subsys_name_pipe)
    except OSError:
        pass
    # 读取这个管道文件
    invasion_subsys_fh = os.open(invasion_subsys_name_pipe, os.O_WRONLY)
    #这一段是调用制作的雄迈的ＩＰＣ的网络摄像头
    # # 7-15-add
    # from xmcext import XMCamera
    # cp = XMCamera("192.168.0.2", 34567, "admin", "ludian@blq", "")
    # cp = XMCamera("192.168.0.4", 34567, "admin", "", "")
    # cp.PrintInfo()
    # cp.login()
    # cp.open()

    # 调用笔记本内置摄像头，所以参数为0，如果有其他的摄像头可以调整参数为1，2
    # 使用笔记本自带的是0
    cap = cv2.VideoCapture(0)
    time.sleep(2)

    warning_counter = 0
    previous_exist_unknown_person = True
    # 7-15-add
    counter = 0
    while True:
        from PIL import Image
        counter = counter + 1
        sucess, img = cap.read()

        # frame = np.asarray(cp.queryframe('array')).reshape(1080, 1920, 3)
        # 将摄像头拍到的图像数据重置成1920x1080分辨率
        frame = cv2.resize(img, (1920, 1080))
        # ret, frame = video_capture.read()
        # 每两帧进行一次人脸识别
        if(counter%2 == 0):
            persons, confidences, bbs = infer(frame, args)
            print("P: " + str(persons) + " C: " + str(confidences))
            cam_dect_name = str(persons)
            try:
                # append with two floating point precision
                confidenceList.append('%.2f' % confidences[0])
            except:
                # If there is no face detected, confidences matrix will be empty.
                # We can simply ignore it.
                pass

            for i, c in enumerate(confidences):
                global cam_confidences
                cam_confidences = c


            # Print the person name and conf value on the frame next to the person
            # Also print the bounding box
            for idx, person in enumerate(persons):
                cv2.rectangle(frame, (bbs[idx].left() * 4, bbs[idx].top() * 4),
                              (bbs[idx].right() * 4, bbs[idx].bottom() * 4), (0, 255, 0), 2)
                # cv2.putText(frame, "{}@{:.2f}".format(person, confidences[idx]),
                #             (bbs[idx].left() * 4, bbs[idx].bottom() * 4 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                #             (255, 255, 255), 1)

            os.write(invasion_subsys_fh, frame.tobytes())
        else:
            continue
        # cv2.imshow('', frame)
        # cv2.waitKey(0)

    cv2.destroyAllWindows()
    cp.close()


class myThread1(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    # Called for every client connecting (after handshake)
    def new_client(self, client, server):
        print("New client connected and was given id %d" % client['id'])
        #server.send_message_to_all("Hey all, a new client has joined us")
        # server.send_message_to_all("YES")

    # Called for every client disconnecting
    def client_left(self, client, server):
        print("Client(%d) disconnected" % client['id'])

    # Called when a client sends a message
    # 通过WebSocket与浏览器进行通信
    def message_received(self, client, server, message):
        global cam_dect_name
        global cam_confidences
        if len(message) > 200:
            message = message[:200] + '..'
        # print("Client(%d) said: %s" % (client['id'], message))
        global cam_confidences_count
        global sum_cam_confidences
        if (cam_dect_name == "[b'xuliang']"):
            sum_cam_confidences = sum_cam_confidences + cam_confidences
            cam_confidences_count = cam_confidences_count + 1
            print(cam_confidences_count)
            # 每检测三帧进行取语音报警
            if (cam_confidences_count % 3 == 0):
                # print(cam_confidences_count)
                if ((sum_cam_confidences) / 3.0 >= 0.7):
                    server.send_message_to_all("JianGe")
                else:
                    server.send_message_to_all("NoPower")
                sum_cam_confidences = 0
                # print(sum_cam_confidences)
        elif (cam_dect_name == "[]"):
            server.send_message_to_all("Normal")
            print(cam_confidences_count)

        # if (cam_dect_name == "[b'xuliang']"):

        #
        #     if(cam_confidences_count%5 == 0):
        #         cam_confidences_count = cam_confidences_count + 1
        #     if(cam_confidences >= 0.95):
        #         server.send_message_to_all("JianGe")
        #     else:
        #         server.send_message_to_all("NoPower")
        # elif (cam_dect_name == "[]"):
        #     server.send_message_to_all("Normal")
        #


    def run(self):
        print("开启线程： " + self.name)
        PORT = 9001
        server = WebsocketServer(PORT, '127.0.0.1')
        server.set_fn_new_client(self.new_client)
        server.set_fn_client_left(self.client_left)
        server.set_fn_message_received(self.message_received)
        # 获取锁，用于线程同步
        threadLock.acquire()
        # print_time1(self.name, self.counter, 1)
        # 释放锁，开启下一个线程
        threadLock.release()
        server.run_forever()
        # print ("开启线程： " + self.name)


class myThread2(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print("开启线程： " + self.name)
        # 获取锁，用于线程同步
        cam_dect()
        #print_time2(self.name, self.counter, 1)
        threadLock.acquire()
        # 释放锁，开启下一个线程
        threadLock.release()


def print_time2(threadName, delay, counter):
    while counter:
        time.sleep(delay)
        print("print_time2:%s: %s" % (threadName, time.ctWime(time.time())))
        counter -= 1


def overlay_transparent(background_img, img_to_overlay_t, x, y, overlay_size=None):
    """
    @brief      Overlays a transparant PNG onto another image using CV2

    @param      background_img    The background image
    @param      img_to_overlay_t  The transparent image to overlay (has alpha channel)
    @param      x                 x location to place the top-left corner of our overlay
    @param      y                 y location to place the top-left corner of our overlay
    @param      overlay_size      The size to scale our overlay to (tuple), no scaling if None

    @return     Background image with overlay on top
    """
    bg_img = background_img.copy()
    if overlay_size is not None:
        img_to_overlay_t = cv2.resize(img_to_overlay_t.copy(), overlay_size)
    # Extract the alpha mask of the RGBA image, convert to RGB
    b, g, r, a = cv2.split(img_to_overlay_t)
    overlay_color = cv2.merge((b, g, r))
    # Apply some simple filtering to remove edge noise
    mask = cv2.medianBlur(a, 5)
    h, w, _ = overlay_color.shape
    roi = bg_img[y:y+h, x:x+w]
    # Black-out the area behind the logo in our original ROI
    img1_bg = cv2.bitwise_and(roi.copy(), roi.copy(),
                              mask=cv2.bitwise_not(mask))
    # Mask out the logo from the logo image.
    img2_fg = cv2.bitwise_and(overlay_color, overlay_color, mask=mask)
    # Update the original image with our new ROI
    bg_img[y:y+h, x:x+w] = cv2.add(img1_bg, img2_fg)
    return bg_img


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dlibFacePredictor',
        type=str,
        help="Path to dlib's face predictor.",
        default=os.path.join(
            dlibModelDir,
            "shape_predictor_68_face_landmarks.dat"))
    parser.add_argument(
        '--networkModel',
        type=str,
        help="Path to Torch network model.",
        default=os.path.join(
            openfaceModelDir,
            'nn4.small2.v1.t7'))
    parser.add_argument('--imgDim', type=int,
                        help="Default image dimension.", default=96)
    parser.add_argument('--cuda', action='store_true', help="Default to use GPU and Cuda.",default=True)
    parser.add_argument(
        '--classifierModel',
        type=str,
        help='The Python pickle representing the classifier. This is NOT the Torch network model, which can be set with --networkModel.',
        default=os.path.join(modelDir,
            'face',
            "IPC1_simple.pkl"))
    args = parser.parse_args()

    align = openface.AlignDlib(args.dlibFacePredictor)
    net = openface.TorchNeuralNet(
        args.networkModel,
        imgDim=args.imgDim,
        cuda=args.cuda)

    threadLock = threading.Lock()
    threads = []

    # 创建新线程
    thread1 = myThread1(1, "Thread-1", 1)
    thread2 = myThread2(2, "Thread-2", 2)

    # 开启新线程
    thread1.start()
    thread2.start()

    # 添加线程到线程列表
    threads.append(thread1)
    threads.append(thread2)

    # 等待所有线程完成
    for t in threads:
        t.join()
    print("退出主线程")
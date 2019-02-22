import cv2
import numpy as np
import time
import os
from matplotlib import pyplot as plt

# 捕获笔记本自带摄像头采集到的图像数据
def camera():
    # 调用笔记本内置摄像头，所以参数为0，如果有其他的摄像头可以调整参数为1，2
    # 使用笔记本自带的是0
    cap = cv2.VideoCapture(0)
    # 使用第二个USB相机是2
    cap = cv2.VideoCapture(2)



    while True:
        # 从摄像头读取图片
        sucess, img = cap.read()
        sucess, img = cap.read()
        # print(img)
        # print(type(img))
        # img = np.asarray(img).reshape(1920,1080,1)
        # print(img)
        # print(type(img))
        # frame = cv2.resize(img, (1920, 1080))

        # 转为灰度图片
        # gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        # 显示摄像头，背景是灰度。
        cv2.imshow("img", img)
        # 保持画面的持续。
        k = cv2.waitKey(1)
        if k == 27:
            # 通过esc键退出摄像
            cv2.destroyAllWindows()
            break
        elif k == ord("s"):
            # 通过s键保存图片，并退出。
            cv2.imwrite("image2.jpg", img)
            cv2.destroyAllWindows()
            break
    # 关闭摄像头
    cap.release()
if __name__=='__main__':
    camera()
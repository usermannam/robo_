# -*-coding:utf-8-*-
import cv2
import platform
import sys
import serial
import time
from threading import Thread

from global_var import Global_var
from Serial import Message
from img_process import Img
from Stage_decision import Stage
from Action_decision import Action

if __name__ == '__main__':
    # cap = None
    print("-------------------------------------")
    print("---- (2020-1-20)  MINIROBOT Corp. ---")
    print("-------------------------------------")

    os_version = platform.platform()
    print(" ---> OS " + os_version)
    python_version = ".".join(map(str, sys.version_info[:3]))
    print(" ---> Python " + python_version)
    opencv_version = cv2.__version__
    print(" ---> OpenCV  " + opencv_version)
    print("-------------------------------------")

    W_View_size = 320  # 320  #640
    H_View_size = 240

    cap = cv2.VideoCapture(0)
    cap.set(3, W_View_size)
    cap.set(4, H_View_size)

    BPS = 4800  # 4800,9600,14400, 19200,28800, 57600, 115200

    # ---------local Serial Port : ttyS0 --------
    # ---------USB Serial Port : ttyAMA0 --------

    # serial_port = serial.Serial('/dev/ttyS0', BPS, timeout=0.01)
    # serial_port.flush()  # serial cls

    # --------------------------- 통신 설정 끝

    gv = Global_var()
    mg = Message(gv)
    lp = Img(gv, cap)
    st = Stage(gv)
    at = Action(gv)

    st.var_init(mg, lp, at)
    at.var_init(mg)


    serial_t = Thread(target=mg.Receiving, args=(gv.serial_port,))
    serial_t.daemon = True
    serial_t.start()
    time.sleep(0.1)
    # ---------------------------
    # First -> Start Code Send
    mg.TX_data_py2(gv.serial_port, 128)

    time.sleep(1)
    while True:
        # video_load()
        if gv.task_step == 1:
            # TX_data_py2(serial_port, 43)
            while True:
                mg.TX_append(gv.down_head)
                if mg.get_down():
                    time.sleep(1)
                    break
            lp.img_process()

        # elif gv.task_step == 2:
        #     gv.task_step = int(input("현재 테스크 2, 다음 테스크 입력바람"))
        # elif gv.task_step == 3:
        #     gv.task_step = int(input("현재 테스크 3, 다음 테스크 입력바람"))
        # else:
        #     gv.task_step = int(input("테스크 잘 못 입력, 다음 테스크 입력바람 (1,2,3)"))


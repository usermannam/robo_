import cv2
import numpy as np
import matplotlib.pyplot as plt

def nothing(x):
    pass

cv2.namedWindow('Binary')
cv2.createTrackbar('threshold', 'Binary', 0, 255, nothing)
cv2.setTrackbarPos('threshold', 'Binary', 127)

cap = cv2.VideoCapture(0)
W_View_size = 320  # 320  #640
H_View_size = 240

cap.set(3, W_View_size)
cap.set(4, H_View_size)

while True:
    ret, img_color = cap.read()
    h, v, c = img_color.shape
    h = int(h * 0.8)  # 발 안보이게 하려고 하단에 짤랐음
    img_color = img_color[:h]  # 발 안보이게 하려고 하단에 짤랐음

    if ret:
        v_ = img_color[:, :, 2]
        v_ = (v_ - np.mean(v_)) / np.std(v_)

        h_ = img_color[:, :, 0]
        h_ = (h_ - np.mean(h_)) / np.std(h_)

        img_color[:, :, 2] = v_
        img_color[:, :, 0] = h_

        cv2.imshow('or', img_color)

        low = cv2.getTrackbarPos('threshold', 'Binary')
        ret,img_binary = cv2.threshold(img_color, low, 360, cv2.THRESH_BINARY)
        img_binary = cv2.cvtColor(img_binary, cv2.COLOR_HSV2BGR)
        img_binary = cv2.cvtColor(img_binary, cv2.COLOR_BGR2GRAY)

        img_binary[img_binary!=255] = 0
        img_binary = cv2.Canny(img_binary, 50, 200, apertureSize=5)
        cv2.imshow('Binary', img_binary)

        img_result = cv2.bitwise_and(img_color, img_color, mask=img_binary)
        cv2.imshow('Result', img_binary)


        if cv2.waitKey(1)&0xFF == 27:
            break

plt.show()
cv2.destroyAllWindows()
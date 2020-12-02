import cv2
import numpy as np
import matplotlib.pyplot as plt

cap = cv2.VideoCapture(0)
W_View_size = 320  # 320  #640
H_View_size = 240

cap.set(3, W_View_size)
cap.set(4, H_View_size)

while True:
    ret, img_color = cap.read()
    img_color = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)  # HSV로 변환
    h, v, c = img_color.shape
    h = int(h * 0.8)                                # 발 안보이게 하려고 하단에 짤랐음
    img_color = img_color[:h]                       # 발 안보이게 하려고 하단에 짤랐음

    if ret:
        plt.cla()
        for i, col in enumerate(['b', 'g', 'r']):
            hist = cv2.calcHist([img_color], [i], None, [256], [0, 256])
            plt.plot(hist, color=col)
        plt.pause(0.001)
        
        # 명도 표준화(standardization)
        v_ = img_color[:, :, 2]
        v_ = (v_ - np.mean(v_)) / np.std(v_)
        
        # 색상 표준화(standardization)
        h_ = img_color[:, :, 0]
        h_ = (h_ - np.mean(h_)) / np.std(h_)

        img_color[:, :, 2] = v_
        img_color[:, :, 0] = h_

        cv2.imshow('or', img_color)

        if cv2.waitKey(1)&0xFF == 27:
            break

plt.show()
cv2.destroyAllWindows()
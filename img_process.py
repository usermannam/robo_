import numpy as np
import cv2

class Img:
    def __init__(self, gv, cap):
        self.gv = gv
        self.cap = cap
        self.size_x = self.gv.size_x
        self.size_y = self.gv.size_y

    # 이미지 전처리
    def img_process(self):
        # 영상 읽기
        while True:
            # 넘어짐 신호 있으면 아무것도 수행 X
            if self.gv.crush:
                continue
            ret, frame = self.cap.read()
            # 이미지 읽기
            if ret:
                # frame = cv2.resize(frame, dsize=(self.size_x, self.size_y), interpolation=cv2.INTER_AREA)
                h, v, c = frame.shape
                frame = frame[:int(h * 0.5)]

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                threshhold = self.img_histogram(gray)
                # 임계값 적용한 이미지
                bin_img = None
                if self.gv.thresh_flag:
                    ret, bin_img = cv2.threshold(gray, threshhold, 255, cv2.THRESH_BINARY_INV)
                else:
                    ret, bin_img = cv2.threshold(gray, threshhold, 255, cv2.THRESH_BINARY)
                
                # 최종 이미지
                f_img = self.noise_delete(bin_img)
                
                # 확인용
                result = np.zeros((gray.shape[0], 256), dtype=np.uint8)
                hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
                cv2.normalize(hist, hist, 0, gray.shape[0], cv2.NORM_MINMAX)
                for x, y in enumerate(hist):
                    cv2.line(result, (x, result.shape[0]), (x, result.shape[0] - y), 255)
                gray = np.hstack([gray, result])

                # 현재 선 상태 판단
                h, v = self.line_distribution(f_img)
                cv2.circle(frame, (h, v), 20, (0, 255, 0), -1)
                cv2.imshow('ov', frame)
                cv2.moveWindow('ov', 0, 0)  # Move it
                cv2.imshow('gv', gray)
                cv2.moveWindow('gv', 500, 0)  # Move it
                cv2.imshow('mv', f_img)
                cv2.moveWindow('mv', 0, 500)

                k = cv2.waitKey(1)
                # esc 키 종료
                if k == 27:
                    break
            else:
                print("error")
                break

    # 노이즈 제거
    def noise_delete(self, img):
        gause_img = cv2.GaussianBlur(img, (5, 5), 0)
        median_img = cv2.medianBlur(gause_img, 5)

        kernel = np.ones((5,5), np.uint8)
        img_mask = cv2.morphologyEx(median_img, cv2.MORPH_OPEN, kernel=kernel)

        return img_mask

    # 선 값 구분 함수 --> 대비로 자동으로 경계값 추출하기
    def img_histogram(self, img):
        hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        cv2.normalize(hist, hist, 0, img.shape[0], cv2.NORM_MINMAX)

        c_1, c_2 = -1, -1
        cx_1, cx_2 = -1, -1
        for x, y in enumerate(hist):
            if c_1 < y:
                c_1 = y

            elif c_2 < y and y < c_1:
                c_2 = y
                cx_2 = x

        return cx_2

    # 선 상태 판단 함수 & 분포도 함수 --> 픽셀값으로 현재 라인 분포 파악하기 (선위치만 판단하서 넘겨주자)
    def line_distribution(self, img):
        # 선 상태 종류
        # 직선, 직석&가로, 가로, 기역자, 대각선, 삼차로
        # 선이 없는 부분
        # 선이 하나가 있는 부분
        # 선이 두개가 있는 부분

        axis_0 = img.sum(axis=0)    # 가로 (컴터에서는 열)
        axis_1 = img.sum(axis=1)    # 세로 (컴터에서는 행)

        # print(axis_0.max(), axis_1.max())
        axis_0 = axis_0 / axis_0.max()      # 상대적인 값(화면에 선이 없을 때는 어떻게 될지 함 생각해 봐야함 ex)노이즈만 있을때
        axis_1 = axis_1 / axis_1.max()      # 상대적인 값

        axis_01, axis_02 = self.line_index(axis_0)
        axis_11, axis_12 = self.line_index(axis_1)

        one_flag = None
        result_h, result_v = None, None
        # 선 한개인 경우 -> 직선 or 가로인 경우임, 대각선 ( 직진일 때만 사용할 듯 회전 중일 때는 그냥 값 무시하기)
        if len(axis_02) == 0 or len(axis_12) == 0:
            one_flag = True
            # 세로로 가득찬 선 한 개 있는 경우
            if len(axis_12) == 0:
                result_h = self.line_position(axis_01)
            
            # 가로로 가득찬 선 한개 있는 경우
            elif len(axis_02) == 0:
                result_v = self.line_position(axis_11)
        
        # 선 두개인 경우 -> 기역자, 삼차로
        else:
            one_flag = False
            result_h = self.plot_analysis(axis_01, axis_02)
            result_v = self.plot_analysis(axis_11, axis_12)

        return result_h, result_v

    # 이미지 내에 후보들 인덱스 추출 함수
    def line_index(self, n):
        m1 = np.where(n > self.gv.max)[0]   # 최대값 가진 x값들
        m2 = np.where(n > self.gv.avg)[0]   # 중간값 가진 x값들(선 2개인 경우 선 한개만 그려진 부분들이 될듯)
        m2 = np.setdiff1d(m2, m1)   # 중간값 가진 x값들 최종

        return m1, m2

    # 분포도 분석 함수
    def plot_analysis(self, n1, n2):
        result = None
        # 분포도
        if n2[0] < n1[0] and n1[-1] < n2[-1]:
            if n2[0] < n2[-1]:
                result = n1[-1]
            else:
                result = n1[0]

        else:
            result = n1[len(n1)//2]

        return result

    # 라인 위치
    def line_position(self, n):
        result = None
        # 센터값 포함하는지
        if np.any(n == self.gv.h_c):
            result = self.gv.c
        # 센터값 포함 안되었을 때
        else:
            # 오른쪽에 있는 경우
            if self.gv.h_2 < n[0]:
                result = self.gv.r
            # 왼쪽에 있는 경우
            else:
                result = self.gv.l

        return result








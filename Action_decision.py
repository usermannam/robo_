import numpy as np
import operator

class Action:
    def __init__(self, global_var):
        self.gv = global_var

        # 화면 해상도
        self.size_y = self.gv.size_y
        self.size_x = self.gv.size_x

        # 허용 범위
        self.degree_range = self.gv.degree_range  # 각도 허용 범위
        self.bottom_range = self.gv.bottom_range  # 선 위치 허용 범위

        # 제어 신호들
        self.Forward = self.gv.Forward  # 앞으로 이동
        self.Right_turn = self.gv.Right_turn  # 오른쪽 회전
        self.Left_turn = self.gv.Left_turn  # 왼쪽 회전
        self.Right_onturn = self.gv.Right_onturn  # 제자리 오른쪽 회전
        self.Left_onturn = self.gv.Left_onturn  # 제자리 왼쪽 회전
        self.down_head = self.gv.down_head  # 머리 최대로 숙이기
        self.up_head = self.gv.up_head  # 머리 초기 상태
        self.stop = self.gv.stop  # 정지 신호

    def var_init(self, message):
        self.mg = message

    # 머리 숙이기 여부 판단
    def head_down(self, line_m, line_b):
        # 머리 숙이기 여부 --> 세로 선이 화면의 가운데 부분에도 걸치는지..
        temp_x = int(self.size_y / 2 / line_m) - int(line_b / line_m)
        if not (0 <= temp_x) and (temp_x < self.size_x):
            # 머리 더 숙이기
            self.mg.TX_append(self.down_head)
            return True
        return False

    # 앞으로 가면서 코너점 추적하기 위한 머리 숙이기
    # def cornor_head_down(self, conor_point):
    #     if conor_point > int(self.size_y / 4 * 3):
    #         TX_append(self.down_head)

    # 다리 전송 신호 결정
    def TX_data_decision(self, degree, e_flag=False):
        # print("decision degree : ", degree)
        # 코너점 돌때
        if e_flag:
            # degree에 따라 90도 회전
            if degree < 0:
                self.mg.TX_append(self.Left_onturn)
            else:
                self.mg.TX_append(self.Right_onturn)

        else:
            # 그냥 직진
            if abs(degree) <= self.degree_range:
                # print("직진")
                self.mg.TX_append(self.Forward)
            # 오른쪽 회전 앞으로 가기
            elif degree < 0:
                self.mg.TX_append(self.Right_turn)
            # 왼쪽 회전 앞으로 가기
            else:
                self.mg.TX_append(self.Left_turn)

    # 라인 복귀하는 함수
    def return_line(self, cross_matrix):
        # 코너점으로 탐색된 것들 중에 가장 y값이 큰걸로 하면 되지 않을까...

        max_row = 0
        base_degree = 90
        return_point = None

        # 교차점이 있으면 그 중에 가장 밑에 있는 점을 교차점으로 판단
        for point in cross_matrix:
            if point[1] > max_row:
                max_row = point[1]
                return_point = point

        # 교차점이 탐색 되었다면
        if return_point is not None:
            des_point = return_point
            degree = np.array(
                (np.arctan2(des_point[1] - 0, des_point[0] - int((self.size_x) / 2)) * 180) / np.pi,
                dtype=np.int32)

            degree -= base_degree
            self.TX_data_decision(degree, True)

        # 탐색 안되었다면 주위 둘러봐야 함.
        # 복귀 포인트 탐색해야 함
        else:
            # 근완땅이 어느쪽에 서 있는지의 값을 기준으로 탐색 방향 정함
            # 일단 임시로 왼쪽으로
            # 탐색 키 번호
            self.mg.TX_append(self.Left_turn)

        # 어느정도 가라는 거를 리턴해야함 (현재는 포인트를 반환)
        # return return_point, False

    # 직선 라인에서 걸을 때 끝지점까지 계산해서 올바른 방향으로 가게하는 함수 --> 꼭지점 까지는 잘감
    def walk_line(self, long_line_point, line_point, line_m, line_b, cross_point):
        cols = int(self.size_x / 2)

        # 각도 생성 --> line_m은 좌표계에서의 기울기임
        # 각도로 오차 구하는게 좀더 현실적
        degree = np.array(
            (np.arctan2(long_line_point[1] - long_line_point[3],
                        long_line_point[0] - long_line_point[2]) * 180) / np.pi,
            dtype=np.int32)

        # 음수 기울기이면 양수로 바꿔줌
        if degree < 0:
            degree += 180

        base_degree = 90  # 기본 선 각도 --> 딱 수직
        des_point = [cols, 0]  # 기준점 --> 딱 바텀 가운데
        cor_point = None  # 꼭지점
        bottom_point = None  # 선의 아래쪽점
        top_point = None  # 선의 위쪽점

        # 세로 선분의 하단과 상단을 구분지어서 바텀과 탑의 좌표로 분배
        if line_point[1] > line_point[3]:
            bottom_point = line_point[:2]
            top_point = line_point[2:]
        else:
            bottom_point = line_point[2:]
            top_point = line_point[:2]

        # 그냥 직선 갈때 --> 3개 구역 탐색 끝나고 나가기 플래그 안 생기면 그냥 끝까지 가야함
        # 중간 코너점 무시하고 끝 코너점까지 가야함
        if not self.gv.exit_flag:
            # 꼭지점 중 가장 위에 있는 꼭지점을 기준으로 감 --> 각 이미지 업데이트마다 가장 상단의 꼭지점 기준으로 ㄱㄱ
            if cross_point is not None:
                # 교차점이 있지만 화면 내에 없을 때.. or 비슷한 라인 2개일 때
                # --> 비슷한 라인이 왜 안되냐?: 경기장내 코너점은 무조건 수직임
                if len(cross_point) != 0:
                    max_point = np.array(cross_point)[:, 1].argmin()
                    max_point = cross_point[max_point]

                # 선분이 여러개 나왔지만 꼭지점이 탐색 안되는 경우
                else:
                    # print("cross_point: ", cross_point)
                    max_point = cross_point[0]

                # 코너점 설정 --> 가장 상단의 코너점으로 설정
                if max_point[1] <= top_point[1]:
                    cor_point = max_point

        # 나갈 때 --> 라인 중간에 있는 꼭지점 잡아야 함
        else:
            # 꼭지점 중 밑에 있는 꼭지점을 기준으로 감
            if cross_point is not None:
                exit_cornor_point = np.array(cross_point)[:, 1].argmax()
                exit_cornor_point = cross_point[exit_cornor_point]

                # 코너점 설정
                if (exit_cornor_point[1] >= top_point[1]) and (exit_cornor_point[1] <= bottom_point[1]):
                    cor_point = exit_cornor_point

        # -------------------------------------------------------------> 코너점 설정 끝
        # -------------------------------------------------------------> 코너점 설정 끝

        flag_bottom_range = False
        # flag_degree_range = False

        # 선 가운데 위치 여부
        diff_bottom_point = bottom_point[0] - cols
        if abs(diff_bottom_point) > self.bottom_range:
            flag_bottom_range = True

        # ------------------------------> 여기부터!!
        # 코너점 안 보이면 현재 라인 기울기만 계산해서 잘 가는지 보고
        if cor_point is None:

            if flag_bottom_range:  # and flag_degree_range:
                # 목표 포인트 잡고 기울기 계산
                # int(cols/2) = line_m*x + line_b --> x = int((cols/2-line_b)/line_m)
                des_point[0] = int((self.size_y / 4 * 3 - line_b) / line_m)
                des_point[1] = int(self.size_y / 4 * 3)
                # 목표 지점 각도 계산
                degree = np.array(
                    (np.arctan2(des_point[1] - 0, des_point[0] - cols) * 180) / np.pi,
                    dtype=np.int32)
                # print("꼭지점 X (바텀 차이)-->", degree)
                # 몇도 차이나는지
                diff_degree = degree - base_degree
                # cv2.line(frame, (cols, self.size_y), (des_point[0], des_point[1]), (255, 0, 0), 4)

                # print("x_degree : ", degree, bottom_point, cols)
                # 대각선 앞으로 신호 보내기
                self.TX_data_decision(diff_degree)

            # 바텀이 차이가 안나더라도 회전 차이는 발생할 수 있음 대각선 앞으로
            else:
                # just forward
                degree -= base_degree

                self.TX_data_decision(degree)

        # 코너점 검출 되었을 때 --> 이때만 머리 숙이는 코드 넣어도 될 듯...
        else:
            # print("코너점 검출 됨")
            des_point = cor_point
            # self.cornor_head_down(cor_point[1])

            degree = np.array(
                (np.arctan2(des_point[1] - 0, des_point[0] - cols) * 180) / np.pi,
                dtype=np.int32)

            # cv2.line(frame, (cols, self.size_x), (des_point[0], des_point[1]), (255, 0, 0), 4)
            # degree -= base_degree
            # 몇도 차이나는지

            # cv2.putText(frame, 'POINT 0'.format(degree), (10, 70), font, fontScale, (0, 0, 255), 2)
            # print("꼭지점 O -->", degree)
            diff_degree = degree - base_degree
            # 코너점 발견 되어도 그냥 직진하는거니까..
            self.TX_data_decision(diff_degree)
            # if flag_bottom_range:
            #     # 코너점 발견 되어도 그냥 직진하는거니까..
            #     self.TX_data_decision(diff_degree)
            # else:
            #     self.TX_data_decision(diff_degree, line_flag=True, frame=frame)

    # 코너점 돌기 함수
    def corner(self, line_point, L_R_flag, e_flag=False):
        de_line = []
        de_point = {}

        # # 라인이 탐색 안된다면
        # if len(line_point) == 0:
        #     self.TX_data_decision(degree, True, e_flag)

        # 라인이 한 개라면
        if len(line_point) == 1:
            de_line = line_point

        # 라인이 두 개 이상이면
        else:
            for index, x in enumerate(line_point):
                # 꼭지점에서 먼 점 가져오기
                # 왼쪽 방향이면
                if L_R_flag:
                    if x[0] > x[2]:
                        de_point[index] = x[2]
                    else:
                        de_point[index] = x[0]
                else:
                    if x[0] < x[2]:
                        de_point[index] = x[2]
                    else:
                        de_point[index] = x[0]

            # 가로선 고르고
            if L_R_flag:
                index = min(de_point.items(), key=operator.itemgetter(1))[0]
                de_line = line_point[index]
            else:
                index = max(de_point.items(), key=operator.itemgetter(1))[0]
                de_line = line_point[index]
        # 일단 임시로
        # de_line 형태 : [array[12,55,69,231], dtype=int32]
        # print("코너에서 라인 : ", de_line[0])
        de_line = de_line[0]
        # print("라인 특정 영역 : ", de_line[0], de_line[1], de_line[2], de_line[3])
        degree = None
        if L_R_flag:
            if de_line[0] < de_line[2]:
                degree = np.array(
                    (np.arctan2(de_line[1] - de_line[3], de_line[0] - de_line[2]) * 180) / np.pi,
                    dtype=np.int32)
            else:
                degree = np.array(
                    (np.arctan2(de_line[3] - de_line[1], de_line[2] - de_line[0]) * 180) / np.pi,
                    dtype=np.int32)
        else:
            if de_line[0] < de_line[2]:
                degree = np.array(
                    (np.arctan2(de_line[3] - de_line[1], de_line[2] - de_line[0]) * 180) / np.pi,
                    dtype=np.int32)
            else:
                degree = np.array(
                    (np.arctan2(de_line[1] - de_line[3], de_line[0] - de_line[2]) * 180) / np.pi,
                    dtype=np.int32)
        degree -= 90
        self.TX_data_decision(degree, e_flag=True)

    # 에외 처리 함수 --> 화면에 선이 탐지 안 될 때
    def except_con(self, conor_flag):
        print("예외 가는 중일 때 처리..")
        # 코너점 회전 중이였을 때
        if conor_flag:
            # 왼쪽 회전
            if self.gv.L_R_flag:
                self.mg.TX_append(self.Left_onturn)
            else:
                self.mg.TX_append(self.Right_onturn)

        # 그냥 가는 중이였을 때
        else:
            # 그냥 대기?
            # self.mg.TX_append(self.Left_onturn)
            pass
        
    def enterence(self, line_point, line_m, cross_point, L_R_flag):
        # 입장시 화살표 값 받고 해당 방향 쪽으로 90도 턴
        # 화살표 방향 변수에 따라서 선 판단...
        # 교차점 기준으로 기울기 낮은 선의 양 끝 점에 따라 판단
        # print("enterence 하는 중")
        min_m = line_m[0]
        min_index = 0

        for index, i in enumerate(line_m):
            if abs(i) < min_m:
                min_m = abs(i)
                min_index = index

        min_point = line_point[min_index]

        cross_point = cross_point[0]

        if min_point[0] < cross_point[0]:
            left_point = min_point[:2]
            right_point = min_point[2:]
        else:
            left_point = min_point[2:]
            right_point = min_point[:2]

        if L_R_flag:
            # degree = np.array(
            #     (np.arctan2(left_point[1] - 0, left_point[0] - int(self.size_y / 2)) * 180) / np.pi,
            #     dtype=np.int32)
            degree = np.array(
                (np.arctan2(left_point[1] - cross_point[1], left_point[0] - cross_point[0]) * 180) / np.pi,
                dtype=np.int32)
        else:
            degree = np.array(
                (np.arctan2(right_point[1] - cross_point[1], right_point[0] - cross_point[0]) * 180) / np.pi,
                dtype=np.int32)

        degree -= 90

        self.TX_data_decision(degree, turn_flag=True)
        return degree
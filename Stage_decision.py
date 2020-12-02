import time

class Stage:
    def __init__(self, global_var):
        self.gv = global_var

    def var_init(self, message, line_move, action_decision):
        self.mg = message
        self.lm = line_move
        self.ad = action_decision

    # 교차점 매트릭스, 화면 채우는 선 포인트(시작, 끝) 리스트, 원래 선 포인트(시작, 끝) 리스트, 선 기울기 리스트, 선 절편 리스트
    def line_condition(self, cross_matrix, long_line_point, line_point, line_m, line_b):

        if self.gv.step == 1:
            # 가로선만 보이는 게 아니라면
            if not self.gv.vertle_line_flag:
                # 코너점 갔다가 다시 세로선 보여서 온거면 다음 스탭으로
                if self.gv.conor_flag:
                    while True:
                        self.mg.TX_append(self.gv.up_head)
                        if self.mg.get_up():
                            self.gv.step = 2
                            self.gv.conor_flag = False
                            print(" 1단계 완료!!!!!")
                            continue
                else:
                    # 기울기 가장 큰 세로선의 성분만 들어감
                    self.ad.walk_line(long_line_point[0], line_point[0], line_m[0], line_b[0], cross_matrix)

            # 가로선만 보이면 바로 턴
            else:
                # 코너 점 돌았다.
                self.gv.conor_flag = True
                # 코너점 돌기 함수
                self.ad.corner(line_point, L_R_flag=self.gv.L_R_flag, e_flag=True)

        # # 직선 가는거
        # elif self.step == 2:
        #     # 일단은 임시로
        #     exit_flag = False
        #     # 앞으로 가다가 --> 코너점에서 멈추고 --> 앞으로 보는거까지
        #
        #     # 가로선만 보이고 머리 다 숙인거 아니라면
        #     if not (self.head_flag and self.vertle_line_flag):
        #         self.walk_line(long_line_point[0], line_point[0], line_m[0], line_b[0], cross_matrix)
        #
        #     # 머리 상태 신호에 따라 결정
        #     self.head_flag_dicision()
        #
        #     # 머리 끝까지 숙였는데도 코너점이 안보이면
        #     # --> 머리 숙이는거는 라인이 안보이거나 코너점을 목표로 찍었을 때만 작동
        #     # 따라서 머리 끝까지 숙인 것과 코너점의 존재 여부로만 판단가능
        #     if self.head_flag and (self.vertle_line_flag or cross_matrix is not None):
        #         # 멈추는 신호
        #         TX_append(self.stop)
        #
        #     # 멈춘 신호 오면 전방 주시
        #     if get_RX_stop():
        #         # 전방 주시
        #         TX_append(self.up_head)
        #         # 찬호한테 넘기는 부분
        #         task_step = 2
        #         # 그 다음에 이 클래스로 들어오면 복귀 부터한다고 명시
        #         self.step = 3
        #
        # # 복귀할 선 탐색하는것도 필요함 --> 근완땅쪽에서 노란색 객체 찾는거 까지 해주면 땡큐
        # # 다시 복귀
        # elif self.step == 3:
        #     # 라인 복귀하다가 --> 코너점에서 멈추고 --> 코너점 돌고
        #     # 머리 다 숙였고 교차점이 없는 상태가 아니라면
        #     if not (self.head_flag and cross_matrix is None):
        #         # 라인 복귀 함수 호출
        #         self.return_line(cross_matrix)
        #
        #     # 머리 상태 신호에 따라 결정
        #     self.head_flag_dicision()
        #
        #     # 머리 다 숙였고 교차점 없다면 --> 코너점 돌기
        #     if self.head_flag and cross_matrix is not None:
        #         # 코너점 돌기
        #         self.corner(line_point, L_R_flag=L_R_flag)
        #
        #         # 직진 or 나가기 분기점
        #         if not exit_flag:
        #             self.step = 2
        #         else:
        #             self.step = 4
        #
        # # 수정 필요 --> step 3에서 왔는데 직진 함수부터 해야할 듯
        # # 나가기
        # elif self.step == 4:
        #     # 머리 다 숙이고 교차점이 하나도 없는
        #     # (세로 선은 있어도 가로선이 거의 사라져서 직선탐색 안될때까지 진행 ㄱㄱ 해야지 딱 턴 하기 좋은 위치) 상태가 아니면 직진
        #     if not (self.head_flag and cross_matrix is None):
        #         # 직진
        #         self.walk_line(long_line_point[0], line_point[0], line_m[0], line_b[0], cross_matrix)
        #
        #     # 앞으로 가다가 멈추는 신호를 줘야하나... 다른 신호들어가면 제어보드에서 알아서 멈추고 그 신호 동작 하도록 ㄱㄱ
        #     # 앞으로 가다가 멈추는 신호를 줘야하나... 다른 신호들어가면 제어보드에서 알아서 멈추고 그 신호 동작 하도록 ㄱㄱ
        #
        #     # 머리 상태 신호에 따라 결정
        #     self.head_flag_dicision()
        #
        #     # 코너점 돌기 ( 위의 조건 반대 ) 또 if를 해서 탐색하는 이유는
        #     # 위의 if와 지금 if 사이에 한번더 신호 왔는지 확인해서 최대한 실시간으로 하려고
        #     if self.head_flag and cross_matrix is not None:
        #         # 나가기 턴이니까 90도 턴하기 위해 e_flag=True로 설정
        #         self.corner(line_point, L_R_flag=L_R_flag, e_flag=True)
        #
        #     # 다 돌았다는 신호 오면
        #     if get_RX_turn():
        #         # 전방 주시
        #         TX_append(self.up_head)
        #         # 찬호한테 넘기는 부분
        #         task_step = 2
        #         # 만약 그 다음에 이 클래스로 들어오면 직진해야함
        #         self.step = 2
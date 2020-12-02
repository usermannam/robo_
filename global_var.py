import serial

class Global_var:
    def __init__(self):
        self.task_step = 1      # 현재 수행해야 하는 연산
        self.L_R_flag = False   # 왼쪽방향 오른쪽방향 (True: 왼쪽, False: 오른쪽)
        self.exit_flag = False       # 다음에는 나간다는 플래그

        self.serial_use = 1
        self.BPS = 4800  # 4800,9600,14400, 19200,28800, 57600, 115200
        self.serial_port = serial.Serial('/dev/ttyS0', self.BPS, timeout=0.01)
        self.serial_port.flush()  # serial cls
        self.Read_RX = 0
        self.receiving_exit = 1
        self.threading_Time = 0.01

        self.RX = []
        self.TX = {}
        self.TX_old = None
        self.crush = False
        self.delay_num = 0

        # 2. 머리 다 숙인 플래그 & 위치 허용 범위 정의
        self.head_flag = False
        self.conor_flag = False
        self.vertle_line_flag = False
        self.degree_range = 30  # 각도 허용 범위
        self.bottom_range = 80  # 선 위치 허용 범위

        # 3. 라인 탐색 --> 상황 단계에 따라서
        self.step = 1

        # 제어 신호들 --- v2
        self.Forward = 33  # 앞으로 이동
        self.Right_turn = 34  # 오른쪽 회전
        self.Left_turn = 35  # 왼쪽 회전
        self.Right_onturn = 36  # 제자리 오른쪽 회전
        self.Left_onturn = 37  # 제자리 왼쪽 회전
        self.down_head = 38  # 머리 최대로 숙이기
        self.up_head = 39  # 머리 초기 상태
        self.stop = 40  # 정지 신호

        # 화면 해상도
        self.size_y = 320
        self.size_x = 240

        # 1. 라인 색
        self.lower_yellow_line = (20, 95, 95)
        self.upper_yellow_line = (30, 180, 180)

        # 1. 라인 색_v2 대비효과를 활용한 버전
        # True면 배경이 선보다 밝은 거
        # False면 선이 배경보다 밝은 거
        self.thresh_flag = True

        # 산포도 기준 값
        self.max = 0.8
        self.avg = 0.4
        self.min = 0.1
        
        # 화면 기준 값
        self.h_c = self.size_x // 2
        self.v_c = self.size_y // 2

        # 선 위치 값
        self.c = 0  # 센터
        self.l = 1  # 왼쪽, 위쪽
        self.r = 2  # 오른쪽, 아래쪽

        #ROI
        self.roi = 0.8
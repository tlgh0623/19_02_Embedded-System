import RPi.GPIO as GPIO
from coapthon.resources.resource import Resource
import threading
import logging as logger
import time as Time

switch = 5      # 스위치
pir = 26        # PIR센서
led = 16        # LED센서

cnt = 0         
flag = 0
count = int(input("알람 설정 : "))

class ObservableResource(Resource):
    
    def __init__(self, name="Obs", coap_server=None):
        super(ObservableResource, self).__init__(name, coap_server, visible=True, observable=True, allow_children=False)
        self.payload = True
        self.period = 5
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pir, GPIO.IN)        # PIR 센서 연결
        GPIO.setup(led, GPIO.OUT)       # LED 모듈 연결
        GPIO.setup(switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # 스위치 연결 및 풀업으로 설정
        self.update(True)

    def render_GET(self, request):
        return self

    def render_POST(self, request):
        self.payload = request.payload
        print(self.payload)
        return self
    
    # 스위치를 누르면 LED OFF
    def switchctrl(self):
        if GPIO.input(switch) == 1: # 스위치가 안눌렸을때
            while True:
                if GPIO.input(switch) == 0: 
                    GPIO.output(led, False)
                    break
                
    # PIR 동작 감지시 LED 점등
    def startpir(self):             
        GPIO.output(led, True)      # LED ON
        self.switchctrl()   # 스위치 작동 함수 실행
        Time.sleep(2)
    
    def update(self, first=False):
        global count,flag,cnt
        if not self._coap_server.stopped.isSet():
            timer = threading.Timer(self.period, self.update)
            timer.setDaemon(True)
            timer.start()
            flag += 5
            if not first and self._coap_server is not None:
                if flag == count :
                # 입력한 시간이 됬을때 pir센서에 감지되면
                    if GPIO.input(pir)==1:
                        # 자리에서 일어나지 않고 더 앉아있는 경우 client로 payload 전달
                        if cnt == 6:
                            temp = cnt*6
                            print(temp,"분을 더 앉아있었습니다.")
                            self.payload = "30분을 더 앉아있었습니다."
                            self._coap_server.notify(self)
                            self.observe_count += 1
                            count = int(input("다시 시간을 입력하세요 : "))
                            Time.sleep(60)
                        # 자리에 있을경우 LED 점등과 계속앉아있는 경우를 위한 카운트 증가
                        # 5분마다 감지를 위한 count값 변경
                        else:
                            self.payload = "자리에 있습니다."
                            print("현재 payload : ",self.payload)
                            self.startpir()
                            cnt+=1
                            Time.sleep(2)                           
                            self._coap_server.notify(self)
                            self.observe_count += 1
                            flag=0
                            count = 300
                # 자리에 없을 경우 payload값 전달
                    else:
                        self.payload = "자리에 없습니다."
                        print("현재 payload : ",self.payload)
                        self._coap_server.notify(self)
                        self.observe_count += 1
                        flag = 0
                        count = int(input("다시 시간을 입력하세요 : "))
                        Time.sleep(60)
                # 입력한 시간이 지나기전에 자리에 있는지 확인
                # 자리에 있는지 없는지 payload 전송
                else:                                            
                    if GPIO.input(pir):
                        self.payload = "알람(전) 자리에 있습니다."
                        print("현재 payload : ", self.payload)
                    else:
                        self.payload = "알람(전) 자리에 없습니다."
                        print("현재 payload : ", self.payload)
                        self._coap_server.notify(self)
                        self.observe_count += 1
                    
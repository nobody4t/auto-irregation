from django.shortcuts import render
import traceback, os
from django.http import JsonResponse, StreamingHttpResponse, FileResponse, HttpResponse, Http404
from . import soil_sensor
from .models import GrassEnvironment, AnimalRecord
from datetime import datetime, timedelta
from django.db import connection
import time, json
from .valve_control import control_watervalve
import threading
import cv2
from .ani_pre import main_det
import base64
import urllib
import tempfile


class GetSensordataandAutoControl:

    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GetSensordataandAutoControl, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        for i in ('hummin','hummax','sendetinterval','loopcount','change_interval_flag','valve_state'):
            if not hasattr(self, i):
                setattr(self, i, 0)

    def SetInitial(self):
        self.hummin = 20
        self.hummax = 60
        self.sendetinterval = 30 # min
        self.loopcount = 0 # 循环计数
        self.change_interval_flag = False # 改变采样间隔标注
        self.valve_state = "close"

    def AutoGetdata(self):
        try:
            while True:
                try:
                    self.loopcount = self.loopcount + 1 
                    if self.loopcount > self.sendetinterval:
                        receive_data = soil_sensor.get_sensor_data

                        current_time = datetime.now()
                        current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')

                        if receive_data[0:6] == "010304":

                            temp10 = int(receive_data[10:14], 16)
                            hum10 = int(receive_data[6:10], 16)

                            if temp10 > 32768:
                                temp10 = temp10 - 65535
                            now_temp_int = temp10 / 10
                            now_hum_int = hum10 / 10

                            now_temp_str = str(now_temp_int)
                            now_hum_str = str(now_hum_int)

                            save_data = GrassEnvironment(Time=current_time, Temp=now_temp_str, Hum=now_hum_str)
                            save_data.save()
                            print(f"{current_time} data:{now_temp_str}℃ {now_hum_str}% saved!")
                        else:
                            print(f"{current_time} get data error!")
                        self.AutoControl()
                        self.loopcount = 0
                except Exception as e:
                    print(f"=== AutoGetdata while 发生错误 ===")
                    print(f"错误类型: {type(e).__name__}")
                    print(f"错误信息: {str(e)}") 
                    print("=== 错误位置 ===")
                    print(traceback.format_exc())
                finally:
                    s_count = 0
                    while s_count < 60:
                        time.sleep(1)
                        if self.change_interval_flag:
                            self.change_interval_flag = False
                            break   
        except Exception as e:
            print(f"=== AutoGetdata 发生错误 ===")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}") 
            print("=== 错误位置 ===")
            print(traceback.format_exc())


    def GetNowData(self, request):
        try:
            try:
                receive_data = soil_sensor.get_sensor_data()

                current_time = datetime.now()
                current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')

                if receive_data[0:6] == "010304":

                    temp10 = int(receive_data[10:14], 16)
                    hum10 = int(receive_data[6:10], 16)

                    if temp10 > 32768:
                        temp10 = temp10 - 65535
                    now_temp_int = temp10 / 10
                    now_hum_int = hum10 / 10

                    now_temp_str = str(now_temp_int)
                    now_hum_str = str(now_hum_int)

                    save_data = GrassEnvironment(Time=current_time, Temp=now_temp_str, Hum=now_hum_str)
                    save_data.save()
                    print(f"{current_time} data:{now_temp_str}℃ {now_hum_str}% saved!")
                else:
                    print(f"{current_time} get data error!")
        
                data_dict = {
                    "temp" : now_temp_str,
                    "hum" : now_hum_str
                }

                response_data = {'message': 'successful',
                                "data" : data_dict}
            except Exception as e:
                print(f"未检测到传感器：{e}")
                latest = GrassEnvironment.objects.latest('Time')
                data_dict = {
                    'time': latest.Time,
                    'temp': latest.Temp,
                    'hum': latest.Hum
                }

                response_data = {'message': 'successful',
                                'data': data_dict}

        except Exception as e:
            print(f"=== GetNowData 发生错误 ===")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}") 
            print("=== 错误位置 ===")
            print(traceback.format_exc())
            response_data = {'message': 'error'}

        finally:
            self.AutoControl()
            return JsonResponse(response_data, content_type='application/json')
        
    
    def AutoControl(self, ):
        try:
            print("Start auto control")
            latest = GrassEnvironment.objects.latest('Time')
            data_dict = {
                'temp': latest.Temp,
                'hum': latest.Hum
            }

            if data_dict['hum'] < self.hummin:
                    control_watervalve("open")
                    self.valve_state = "open"
            elif data_dict['hum'] > self.hummax:
                    control_watervalve("close")
                    self.valve_state = "close"
        except Exception as e:
            print(f"=== AutoControl 发生错误 ===")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}") 
            print("=== 错误位置 ===")
            print(traceback.format_exc())

    def ValveControl(self, request):
        try:
            byte_data = request.body.decode('utf-8')
            data = json.loads(byte_data).get("content")

            if data.get('operate') == 'open':
                control_watervalve("open")
                self.valve_state = "open"
            elif data.get('operate') == 'close':
                control_watervalve("close")
                self.valve_state = "close"

            state_data = {
                "state" : self.valve_state
            }
         
            response_data = {'message': 'successful',
                            "data": state_data}

        except Exception as e:
            print(f"=== ValveControl 发生错误 ===")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}") 
            print("=== 错误位置 ===")
            print(traceback.format_exc())
            response_data = {'message': 'error'}

        finally:
            return JsonResponse(response_data, content_type='application/json')


    def ChangeThreshold(self, request):
        try:
            byte_data = request.body.decode('utf-8')
            data = json.loads(byte_data).get("content")
            
            if data.get('type') == 'min':
                self.hummin = int(data.get('value'))

            elif data.get('type') == 'max':
                self.hummax = int(data.get('value'))

            threshold = {
                "min" : self.hummin,
                "max" : self.hummax
            }

            response_data = {'message': 'successful',
                            "data": threshold}

        except Exception as e:
            print(f"=== GetSensorData 发生错误 ===")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}") 
            print("=== 错误位置 ===")
            print(traceback.format_exc())
            response_data = {'message': 'error'}

        finally:
            return JsonResponse(response_data, content_type='application/json')


    def ChangeInterval(self, request):
        try:
            byte_data = request.body.decode('utf-8')
            data = json.loads(byte_data).get("content")

            if data.get('type') == 'changeinterval':
                self.sendetinterval = int(data.get('value'))
                self.change_interval_flag = True

            interval = {
                "threshold" : self.sendetinterval,
            }

            response_data = {'message': 'successful',
                            "data": interval}

        except Exception as e:
            print(f"=== GetSensorData 发生错误 ===")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}") 
            print("=== 错误位置 ===")
            print(traceback.format_exc())
            response_data = {'message': 'error'}

        finally:
            return JsonResponse(response_data, content_type='application/json')


def GetSensorData(request):
    try:

        latest = GrassEnvironment.objects.latest('Time')
        data_dict = {
            'time': latest.Time,
            'temp': latest.Temp,
            'hum': latest.Hum
        }

        response_data = {'message': 'successful',
                         'data': data_dict}

    except Exception as e:
        print(f"=== GetSensorData 发生错误 ===")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}") 
        print("=== 错误位置 ===")
        print(traceback.format_exc())
        response_data = {'message': 'error'}

    finally:
        return JsonResponse(response_data, content_type='application/json')

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone

class ProcessImage:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ProcessImage, cls).__new__(cls, *args, **kwargs)
            # cls._instance.SetInitial()
        return cls._instance

    def __init__(self):
        for i in ('frame', 'animal_buffer', 'detflag', 'send2url_flag'):
            if not hasattr(self, i):
                setattr(self, i, 0)

    def SetInitial(self):
        self.frame = None
        self.animal_buffer = None
        self.detflag = False
        self.send2url_flag = False
        # self.channel_layer = get_channel_layer()

        # def test():
        #     while True:
        #         time.sleep(5)
        #         print("test")
        #         self.notify_new_record("new")
        # test_thread = threading.Thread(target=test,daemon=True)
        # test_thread.start()

    # def notify_new_record(self, message):
    #     """通过WebSocket通知新记录"""
    #     async_to_sync(self.channel_layer.group_send)(
    #         "animal_records",  # 与consumer中的组名一致
    #         {
    #             "type": "new.record",
    #             "message": message
    #         }
    #     )

    def GetFrame(self):
        try:
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

            camera_FPS = int(cap.get(cv2.CAP_PROP_FPS))
            print(f"get fps:{camera_FPS}")
            print(f"get width:{cap.get(cv2.CAP_PROP_FRAME_WIDTH)},height:{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

            # frame_count = 0
            # start_time = time.time()
            while True:
                try:
                    ret, frame = cap.read()

                    if ret:
                        self.frame = frame
                        self.detflag = True
                        self.send2url_flag = True
                    else:
                        self.detflag = False
                        self.send2url_flag = False
                    # cv2.imwrite("/home/pi/Desktop/auto_irrigate/web/temp/test.jpg", frame)
                    # frame_count = frame_count + 1
                    # print(f"fps:{frame_count / (time.time() - start_time)}")


                except Exception as e:
                    print(f"=== DetAnimal 获取图像 发生错误 ===")
                    print(f"错误类型: {type(e).__name__}")
                    print(f"错误信息: {str(e)}") 
                    print("=== 错误位置 ===")
                    print(traceback.format_exc())
        except Exception as e:
            print(f"=== GetFrame 发生错误 ===")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}") 
            print("=== 错误位置 ===")
            print(traceback.format_exc())

        finally:
            cap.release()

    def DetectAnimal(self):
        try:
            while True:
                if self.detflag:
                    # self.frame = cv2.imread("/home/pi/Desktop/auto_irrigate/lang.jpg")

                    _, buffer = cv2.imencode('.jpg', self.frame)
                    
                    # 2. 转换为 Base64 字符串
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # 3. 对 Base64 进行 URL 安全编码
                    frame_urlsafe = urllib.parse.quote_plus(frame_base64)
                    det_result = main_det(frame_urlsafe)

                    result_array = det_result["result"]
                    print(f"Detect animal result: {result_array}")
                    if (len(result_array) > 0):
                        first_animal_name = result_array[0]["name"]
                        if first_animal_name == "非动物":
                            continue
                        if first_animal_name != self.animal_buffer:
                            current_time = datetime.now()
                            current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                            save_data = AnimalRecord(Time=current_time, Record=first_animal_name)
                            save_data.save()
                            print(f"{current_time} found:{first_animal_name}")
                            self.animal_buffer = first_animal_name
                            self.detflag = False

                            # 更新html
                            # self.notify_new_record("new")

        except Exception as e:
            print(f"=== DetectAnimal 发生错误 ===")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}") 
            print("=== 错误位置 ===")
            print(traceback.format_exc())


    def CreatVideo(self):
        while True:
            try:
                if self.send2url_flag:
                    _, jpeg = cv2.imencode('.jpg', self.frame)
                    # print("there")
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
            except Exception as e:
                print(f"=== CreatVideo 发生错误 ===")
                print(f"错误类型: {type(e).__name__}")
                print(f"错误信息: {str(e)}") 
                print("=== 错误位置 ===")
                print(traceback.format_exc())
                

    def SendVideoStream(self, request):
        try:
            print('start send img')
            return StreamingHttpResponse(iter(self.CreatVideo()), content_type='multipart/x-mixed-replace; boundary=frame')
        except Exception as e:
            print(f"=== SendVideoStream 发生错误 ===")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}") 
            print("=== 错误位置 ===")
            print(traceback.format_exc())



def Get30AnimalRecords(request):
    
    try:
        latest_time_soil = AnimalRecord.objects.order_by('-Time')[:30]

        data_dict = {
            "time" : [i.Time
                      for i in latest_time_soil],
            "record" : [i.Record
                      for i in latest_time_soil]
        }

        response_data = {'message': 'successful',
                         'data': data_dict}

    except Exception as e:
        print(f"=== PostRecongnitionContent 发生错误 ===")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}") 
        print("=== 错误位置 ===")
        print(traceback.format_exc())
        response_data = {'message': 'error'}

    finally:
        return JsonResponse(response_data, content_type='application/json')

def GeneralTXT(request):
    try:
        # 创建临时文件夹（如果不存在）
        temp_dir = "./web/temp"

        # 解析POST数据
        byte_data = request.body.decode('utf-8')
        data = json.loads(byte_data).get("content")
        download_date = data.get("date")

        target_date = datetime.strptime(download_date, '%Y-%m-%d').date()
        next_day = target_date + timedelta(days=1)
        
        sensor_records = GrassEnvironment.objects.filter(
            Time__range=[target_date, next_day]
        )

        animal_records = AnimalRecord.objects.filter(
            Time__range=[target_date, next_day]
        )
        
        filename = f"report_{download_date}.txt"
        filepath = os.path.join(temp_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"{download_date} 数据报告\n\n")


        with open(filepath, 'a', encoding='utf-8') as f:
            for record in sensor_records:
                f.write(f"时间:{record.Time} 温度:{record.Temp}℃ 湿度:{record.Hum}%\n")

            f.write("\n\n")
            for record in animal_records:
                f.write(f"时间:{record.Time} 危险动物:{record.Record}\n")
        
        current_url = request.build_absolute_uri()
        web_url = current_url.replace('generaltxt/', '')

        download_url = f"{web_url}dltxt/{filename}"

        # print(download_url)
        response_data = {'message': 'successful',
                         'download_url': download_url}
        
    except Exception as e:
        print(f"=== PostRecongnitionContent 发生错误 ===")
        print(f"错误类型: {type(e).__name__}")  # 错误类型（如 ValueError, KeyError）
        print(f"错误信息: {str(e)}")            # 错误描述
        print("=== 错误位置 ===")
        print(traceback.format_exc())           # 完整的错误堆栈（包括文件名和行号）
        response_data = {'message': 'error'}

    finally:
        return JsonResponse(response_data, content_type='application/json')
        

def download_txt(request, filename):
    """
    功能描述：下载TXT文件的处理函数
    """
    # 定义文件路径（可根据需要调整路径）
    file_path = f"web/temp/{filename}"
    
    # 检查文件是否存在
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as txt_file:
                response = HttpResponse(
                    txt_file.read(),
                    content_type='text/plain'  # 修改为TXT文件的内容类型
                )

            if os.path.exists(file_path):
                try:
                    os.remove(file_path)  # 删除文件
                    # print("文件删除成功")
                except Exception as e:
                    print(f"删除文件时出错: {e}")
            else:
                print("文件不存在")
                
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            return HttpResponse(f"文件读取错误: {str(e)}", status=500)
    else:
        # 可以返回404错误，或者更友好的错误页面
        raise Http404("请求的文件不存在")











try:
    # 开启传感器检测线程
    GetSensordataandAutoControl().SetInitial()
    auto_det_data_thread = threading.Thread(target=GetSensordataandAutoControl().AutoGetdata, daemon=True)
    auto_det_data_thread.start()

    # 开启摄像头线程
    ProcessImage().SetInitial()
    auto_get_frame_thread = threading.Thread(target=ProcessImage().GetFrame, daemon=True)
    auto_get_frame_thread.start()

    # 开启检测程序线程
    auto_det_animal_thread = threading.Thread(target=ProcessImage().DetectAnimal, daemon=True)
    auto_det_animal_thread.start()

except Exception as e:
    print(f"=== view 发生错误 ===")
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {str(e)}") 
    print("=== 错误位置 ===")
    print(traceback.format_exc())


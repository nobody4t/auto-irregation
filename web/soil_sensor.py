import serial
import time


def get_sensor_data():
    try:
        ser = serial.Serial(
            port='/dev/ttyAMA0',  # 树莓派上的串口设备
            baudrate=115200,     # 波特率，根据你的设备调整
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1             # 读取超时时间(秒)
        )

        hex_data = '010300000002C40B'
        data_to_send = bytes.fromhex(hex_data)
        
        # print(f"发送数据: {data_to_send.hex().upper()}")
        
        ser.write(data_to_send)
        time.sleep(0.1)
        
        received_data = ser.read_all()
        
        if received_data:
            print(f"接收sensor数据: {received_data.hex().upper()}")
            return received_data.hex()
        else:
            print("未接收到数据")
            return None

    except Exception as e:
        print(f"get_sensor_data 发生错误: {e}")

    finally:
        ser.close()


if __name__=="__main__":
    get_sensor_data()
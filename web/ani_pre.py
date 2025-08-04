import requests
import base64
import urllib
import cv2

API_KEY = "spCG3iUVI65aLJKPEJ0iA2jN"
SECRET_KEY = "Q384CQ7lZLYD8k4QQS0wbjz5dOdwowiw"

def main_det(content):

    url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/animal?access_token=" + get_access_token()
    
    # path = "lang.jpg"
    # path = img_path
    # with open(path, "rb") as f:
    #     content = base64.b64encode(f.read()).decode("utf8")

    # content = urllib.parse.quote_plus(content)
    payload='image='+content
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))
    
    # print(f"Detect animal :{response.json()}")
    return response.json()

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

if __name__ == '__main__':

    import time
    start_time = time.time()
    frame = cv2.imread("pichong.jpg")
    _, buffer = cv2.imencode('.jpg', frame)
    
    # 2. 转换为 Base64 字符串
    frame_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # 3. 对 Base64 进行 URL 安全编码
    frame_urlsafe = urllib.parse.quote_plus(frame_base64)
    main_det(frame_urlsafe)
    print(time.time()-start_time)

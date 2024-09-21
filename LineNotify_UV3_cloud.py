#在pythonanywhere中執行(測試成功，可在網頁中每日跑出資料)
import requests

# 設定中央氣象局的API的Token
CWA_API_KEY = 'CWA-9C38AD42-6BD5-4C1A-9F2D-99C9FEF21D9D'
# UV 指數 API 的 URL
UV_api_url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0005-001?Authorization={CWA_API_KEY}&limit=20&format=JSON'

# 取得 UV 指數資料
def get_UV_data():
    response = requests.get(UV_api_url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("無法取得 UV 指數資料")
        return None

# 將訊息推送到 LINE Notify
def send_line_notify(LINE_NOTIFY_TOKEN, message, image_url=None):
    headers = {
        "Authorization": f"Bearer {LINE_NOTIFY_TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {'message': message}
    line_notify_url = 'https://notify-api.line.me/api/notify'

    # 發送圖片
    if image_url:
        image_payload = {
            'message': 'UV 指數報告圖片:',
            'imageThumbnail': image_url,
            'imageFullsize': image_url
        }
        response = requests.post(line_notify_url, headers=headers, params=image_payload)

    # 發送訊息
    response = requests.post(line_notify_url, headers=headers, params=payload)
    if response.status_code == 200:
        print("成功推送訊息到 LINE")
    else:
        print("推送失敗，請檢查 Token 或訊息格式")

# 分析 UV 指數並產生警示訊息
def uv_protection_measures(data):
    try:
        # 假設台北市的 UV 指數資料
        date = data["records"]["weatherElement"]["Date"]
        UVIndex_str = data["records"]["weatherElement"]["location"][6]["UVIndex"] #"466920":台北市
        UVIndex = int(UVIndex_str)
        
        if UVIndex <= 2:
            level = "低量級"
            protection = "配戴太陽眼鏡，如在雪地加強防曬"
        elif 3 <= UVIndex <= 5:
            level = "中量級"
            protection = "穿戴帽子、太陽眼鏡、防曬霜"
        elif 6 <= UVIndex <= 7:
            level = "高量級"
            protection = "使用防曬霜，減少在陽光下活動"
        elif 8 <= UVIndex <= 10:
            level = "過量級"
            protection = "採取所有防護措施，避免戶外活動"
        else:
            level = "危險級"
            protection = "極度避免戶外活動"

        # 組合訊息
        message = (f"台北市 UV 指數報告: {date}\n"
                   f"UV 指數: {UVIndex}\n"
                   f"暴露等級: {level}\n"
                   f"防護措施: {protection}")
        return message
    except Exception as e:
        print(f"資料解析失敗: {e}")
        return "無法取得 UV 指數資料"

# 主程序
def main():
    # 獲取 UV 指數資料
    data = get_UV_data()
    if data is not None:
        # 生成訊息
        message = uv_protection_measures(data)
        # 發送到 LINE Notify
        LINE_NOTIFY_TOKEN = 'EqQwaBm1gl6xto6M990xmsW6bOsv7IFfictKw9ixXnZ'  # 替換為你的 Line Notify Token
        send_line_notify(LINE_NOTIFY_TOKEN, message)
    else:
        print("無法取得資料，停止發送訊息")

# 執行主程序
main()

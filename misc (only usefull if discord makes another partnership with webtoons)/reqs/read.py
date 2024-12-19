import requests
from get_NEO import get_neo
from sign import sign_url
from secrets import token_urlsafe
from time import time
from random_header_generator import HeaderGenerator

def getcookies():
    return {
        "wtu"                : token_urlsafe(24),
        "locale"             : "en",
        "needGDPR"           : "true",
        "needCCPA"           : "false",
        "needCOPPA"          : "false",
        "countryCode"        : "RO",
        "timezoneOffset"     : "+3",
        "ctZoneId"           : "Europe/Bucharest",
        "wtv"                : "1",
        "wts"                : str(int(time() * 1000)),
        "__cmpconsentx47472" : f"{token_urlsafe(2)}_{token_urlsafe(3)}_{token_urlsafe(25)}",
        "__cmpcccx47472"     : token_urlsafe(18),
        "_fbp"               : "fb.1.1684479996310.2019224647",
        "_scid"              : "858a934e-433c-4e07-b4c3-c1a1b9becc34",
        "_gid"               : "GA1.2.1016427982.1684479996",
        "_tt_enable_cookie"  : "1",
        "_ttp"               : "2dlVmcQxdz_oQTW_6zMA2eNlFy3",
        "_scid_r"            : "858a934e-433c-4e07-b4c3-c1a1b9becc34",
        "_ga"                : "GA1.1.1939944414.1684479996",
        "_ga_ZTE4EZ7DVX"     : "GS1.1.1684486049.2.0.1684486049.60.0.0",
    }

def read_all(email, password):
    for i in range(1, 11):
        try:
                ses = get_neo(email, password)
                headers = {
                    "cookie": f"NEO_SES={ses}",
                    "user-agent": "nApps (Android 14; sdk_gphone64_x86_64; linewebtoon; 3.4.9)",
                    "wtu": token_urlsafe(24),
                    "host": "global.apis.naver.com",
                    "connection": "Keep-Alive",
                    "accept-encoding": "gzip",
                    "if-modified-since": "Sat, 07 Dec 2024 10:13:17 GMT"
                }
                url = sign_url(f"https://global.apis.naver.com/lineWebtoon/webtoon/eventReadLog.json?v=2&webtoonType=WEBTOON&titleNo=2705&episodeNo={str(i)}&serviceZone=GLOBAL&language=en&locale=en&platform=APP_ANDROID")
                cookies = {
                    "NEO_SES": ses
                }
                response = requests.get(url, cookies=cookies, headers=headers).json()

                if response['message']['result']["progressType"] != "NONE":
                    headers = HeaderGenerator()() 
                    headers.update({
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'host': 'm.webtoons.com',
                        'x-requested-with': 'com.naver.linewebtoon',
                    })
                    cookies = getcookies()
                    cookies.update({
                        "NEO_SES": ses
                    })

                    response = requests.get(response['message']['result']["pageUrl"], headers=headers, allow_redirects=False, cookies=cookies)
                    if '<title>Event</title>' in response.text:
                        print("success")

        except Exception as e:
            print(e)
            return None

print(read_all("jlwokpkvwbukcwheabcbgvaoxp@mailnesia.com", "fywgq1n7pxye"))


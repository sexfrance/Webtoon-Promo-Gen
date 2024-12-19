import requests
from time import time
from secrets import token_urlsafe
from get_NEO import get_neo
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


def claim(email, password):
    url = "https://m.webtoons.com/app/promotion/saveSubmitPayload"
    
    payload = {
        "eventNo": 5362,
        "email": email
    }
    
    headers = HeaderGenerator()() 
    headers.update({
        "host": "m.webtoons.com",
        "origin": "https://m.webtoons.com",
        "x-requested-with": "com.naver.linewebtoon",
        "referer": "https://m.webtoons.com/app/promotion/read/DiscordPhase2-Reading-December2024_Real_Fixed_NewCodes/progress?platform=APP_ANDROID",
                    })
    
    cookies = getcookies()
    cookies.update({
                        "NEO_SES": get_neo(email, password)
                    })

    response = requests.post(url, json=payload, headers=headers)
    if response.json() == True:
     return True
    
    return False
import requests
from get_NEO import get_neo 
from sign import sign_url

def get_CHK(email, password):
    cookies = {
        'NEO_SES': get_neo(email, password),
    }

    response = requests.get(
        sign_url('https://global.apis.naver.com/lineWebtoon/webtoon/getUserPolicyStatus?policyType=CANVAS_TERMS_OF_USE&serviceZone=GLOBAL&v=1&language=en&locale=en&platform=APP_ANDROID'),
        cookies=cookies,
    )
    return response.headers['Set-Cookie'].split(';')[0].split('=')[1].strip('"')

print(get_CHK('whykktjwtwcpmdfywbgwsbwezw@mailnesia.com', 'w5w6yzjrcdnb'))
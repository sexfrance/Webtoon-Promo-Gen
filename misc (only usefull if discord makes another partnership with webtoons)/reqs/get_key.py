import requests

def get_key():
    response = requests.get("https://www.webtoons.com/member/login/rsa/getKeys")
    return response.json()

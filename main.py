import tls_client
import random
import string
import pytz
import asyncio
import json
import re

from functools import lru_cache
from mailtmwrapper import MailTM
from logmagix import Logger, Home
from hmac import new
from urllib.parse import quote
from base64 import b64encode
from hashlib import sha1
from time import time, sleep
from secrets import token_urlsafe
from rsa import PublicKey, encrypt as rsae
from binascii import hexlify
from random_header_generator import HeaderGenerator

DEBUG = True

home = Home("Webtoon Promo Gen", "center", credits="discord.cyberious.xyz")
log = Logger() 

class MailMonitorClient:
    def __init__(self, host='127.0.0.1', port=8887):
        self.host = host
        self.port = port
    
    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
    
    async def add_inbox(self, inbox_name, token, account_id):
        message = {
            "action": "add_inbox",
            "inbox_name": inbox_name,
            "token": token,
            "account_id": account_id
        }
        self.writer.write(json.dumps(message).encode())
        await self.writer.drain()
        
        response = await self.reader.read(1024)
        return json.loads(response.decode())
    
    async def close(self):
        if hasattr(self, 'writer'):
            self.writer.close()
            await self.writer.wait_closed()

async def generate_email():
    username = f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=44))}"
    email = f"{username}@freesourcecodes.com"
    return email

async def generate_password():
    password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?/", k=16))
    return password

async def create_mail(email, password):
    response = MailTM().create_account(email, password)
    if DEBUG:
        log.debug(f"MailTM response: {response}")
    
    if response == 429:
        log.warning("Rate limited, waiting 5 seconds...")
        await asyncio.sleep(5)
        response = MailTM().create_account(email, password)

    if response and isinstance(response, dict):
        account_id = response.get('id')
        if account_id:
            return account_id, email
    return None, None

def chrlen( n: str) -> str:
        return chr(len(n))

def sign_url(uri):
    sign_key = b"gUtPzJFZch4ZyAGviiyH94P99lQ3pFdRTwpJWDlSGFfwgpr6ses5ALOxWHOIT7R1"
    mac = new(sign_key, digestmod=sha1)
    stamp = str(int(time() * 1000))
    
    message = uri[:min(255, len(uri))] + stamp
    mac.update(message.encode('utf-8'))
    
    md = quote(b64encode(mac.digest()))
    separator = '&' if '?' in uri else '?'
    
    return f"{uri}{separator}msgpad={stamp}&md={md}"

@lru_cache(maxsize=128)
async def get_neo_cached(session, email, password):
    if DEBUG:
        log.debug(f"Getting NEO session for email: {email}")
    json = await get_key(session)
    if DEBUG:
        log.debug(f"Got key response: {json}")
    
    url = "https://global.apis.naver.com/lineWebtoon/webtoon/loginById.json"
    payload = {
        "serviceZone": "GLOBAL",
        "encpw": await encrypt(json, email, password),
        "loginType": "EMAIL",
        "v": "3",
        "language": "en",
        "encnm": json["keyName"]
    }
    if DEBUG:
        log.debug(f"Sending login request with payload: {payload}")
    response = await asyncio.to_thread(session.post, url, data=payload)
    if DEBUG:
        log.debug(f"Login response status: {response.status_code}")
        log.debug(f"Login response headers: {dict(response.headers)}")
        log.debug(f"Login response body: {response.text}")
    
    ses = response.json()["message"]["result"]["ses"]
    return ses

async def get_neo(session, email, password):
    return await get_neo_cached(session, email, password)

async def get_chk(neo_ses, session):
    cookies = {
        'NEO_SES': neo_ses,
    }

    response = session.get(
        sign_url('https://global.apis.naver.com/lineWebtoon/webtoon/getUserPolicyStatus?policyType=CANVAS_TERMS_OF_USE&serviceZone=GLOBAL&v=1&language=en&locale=en&platform=APP_ANDROID'),
        cookies=cookies,
    )
    return response.headers['Set-Cookie'].split(';')[0].split('=')[1].strip('"')

async def get_email_message_id(token, max_retries=5):
    if DEBUG:
        log.debug(f"Checking mailbox")
    
    for attempt in range(max_retries):
        if attempt > 0:
            await asyncio.sleep(1.5)
        messages = MailTM(token).get_messages()

        if messages == 429:
            log.warning("Rate limited, waiting 5 seconds...")
            await asyncio.sleep(5)
            messages = MailTM(token).get_messages()

        if not isinstance(messages, list):
            log.failure(f"Unexpected type for messages: {type(messages)}. Messages: {messages}")
            continue
    
        if DEBUG:
            log.debug(f"Messages received: {messages}")

        if messages:
            for message in messages:
                msg_id = message.get('id')
                subject = message.get('subject')
                if subject and '[WEBTOON] Verification Email' in subject:
                    return msg_id
        
        log.info(f"No verification email found, attempt {attempt + 1}/{max_retries}")
    
    return None

async def get_verification_link(token, message_id):
    message = MailTM(token).get_message_by_id(message_id)
    
    if not message:
        log.error("Failed to retrieve message. Message might be None.")
        return None

    content = message.get('text', '')
    if not content and 'html' in message and message['html']:
        content = message['html'][0]

    try:
        link_match = re.search(r'https?://[^\s\]]+email-verification[^\s\]]+', content)
        if link_match:
            verification_link = link_match.group(0)
            log.success(f"Verification link found: {verification_link}")
            return verification_link
        else:
            log.warning("Verification link not found in the message content.")
            return None
    except Exception as e:
        log.error(f"Error extracting verification link: {e}")
        return None
    
async def verify_email(session, verify_link):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'fr-FR,fr;q=0.9',
        'priority': 'u=0, i',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"15.0.0"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
    }
    verify_link = verify_link.replace("m.webtoons.com", "www.webtoons.com")
    verify_link = verify_link + "&webtoon-platform-redirect=true"

    if DEBUG:
        log.debug(f"Verifying email with link: {verify_link}")
        
    response = await asyncio.to_thread(session.get, verify_link, headers=headers)
    
    if DEBUG:
        log.debug(f"Verification response status: {response.status_code}")
        log.debug(f"Verification response headers: {dict(response.headers)}")

    if response.status_code == 302 and 'Set-Cookie' in response.headers:
        if 'email_vr=EMAIL_JOIN' in response.headers['Set-Cookie']:
            return True
    elif response.status_code == 302 and "EXPIRED" in str(response.headers):
        log.warning("Expired Link")
    return False

async def encrypt(json, mail, pw):
    string = f"{chrlen(json['sessionKey'])}{json['sessionKey']}{chrlen(mail)}{mail}{chrlen(pw)}{pw}".encode()
    mod = int(json['nvalue'], 16)
    evl = int(json['evalue'], 16)
    pbk = PublicKey(evl, mod)
    out = rsae(string, pbk)
    return hexlify(out).decode('utf-8')

async def get_key(session):
    response = await asyncio.to_thread(
        session.get,
        "https://www.webtoons.com/member/login/rsa/getKeys"
    )
    return response.json()

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

async def read_all(session, neo_ses):
    if DEBUG:
        log.debug(f"Starting read_all with NEO_SES: {neo_ses}")
    
    episodes_to_read = [2, 8]
    
    async def read_episode(episode):
        if DEBUG:
            log.debug(f"Reading episode {episode}")
        try:
            headers = {
                "cookie": f"NEO_SES={neo_ses}",
                "user-agent": "nApps (Android 14; sdk_gphone64_x86_64; linewebtoon; 3.4.9)",
                "wtu": token_urlsafe(24),
                "host": "global.apis.naver.com",
                "connection": "Keep-Alive",
                "accept-encoding": "gzip",
                "if-modified-since": "Sat, 07 Dec 2024 10:13:17 GMT"
            }
            url = sign_url(f"https://global.apis.naver.com/lineWebtoon/webtoon/eventReadLog.json?v=2&webtoonType=WEBTOON&titleNo=2705&episodeNo={str(episode)}&serviceZone=GLOBAL&language=en&locale=en&platform=APP_ANDROID")
            
            if DEBUG:
                log.debug(f"Reading episode with URL: {url}")
                log.debug(f"Headers: {headers}")
            
                cookies = {
                    'NEO_SES': neo_ses,
                    'NEO_CHK': await get_chk(neo_ses, session),
                    }
            
            response = await asyncio.to_thread(
                session.get,
                url,
                cookies=cookies,
                headers=headers
            )
            
            if DEBUG:
                log.debug(f"Read episode response status: {response.status_code}")
                log.debug(f"Read episode response headers: {dict(response.headers)}")
                log.debug(f"Read episode response body: {response.text}")
            
            response_json = response.json()

            if response_json['message']['result']["progressType"] != "NONE":
                headers = HeaderGenerator()()
                headers.update({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Host': 'm.webtoons.com',
                    'X-requested-with': 'com.naver.linewebtoon',
                    "User-agent": "nApps (Android 14; sdk_gphone64_x86_64; linewebtoon; 3.4.9)",
                    "Wtu": token_urlsafe(24),
                    "Host": "global.apis.naver.com",
                    "Connection": "Keep-Alive",
                    "Accept-encoding": "gzip",
                })
                cookies = getcookies()
                cookies.update({"NEO_SES": neo_ses})

                response = await asyncio.to_thread(
                    session.get,
                    response_json['message']['result']["pageUrl"],
                    headers=headers,
                    allow_redirects=False,
                    cookies=cookies
                )
                
                if '<title>Event</title>' in response.text:
                    log.success(f"Successfully saved checkpoint for episode {episode}")
                    if 'Set-Cookie' in response.headers:
                        cookies_header = response.headers['Set-Cookie']
                        for cookie in cookies_header:
                            if 'SDC=' in cookie:
                                sdc = cookie.split('SDC=')[1].split(';')[0]
                                return True, sdc
                
        except Exception as e:
            log.failure(f"Error reading episode {episode}: {e}")
        
        return False, None

    results = await asyncio.gather(*[read_episode(episode) for episode in episodes_to_read])
    
    for success, sdc in results:
        if success and sdc:
            return True, sdc
    
    return False, None

async def claim(session, email, neo_ses, sdc):
    if DEBUG:
        log.debug(f"Attempting to claim promo for email: {email}")
        log.debug(f"Using NEO_SES: {neo_ses}")
        log.debug(f"Using SDC: {sdc}")
    
    payload = {
        "eventNo": 5362,
        "email": email
    }
    
    headers = HeaderGenerator()()
    headers.update({
        "Host": "m.webtoons.com",
        "Origin": "https://m.webtoons.com",
        "X-requested-with": "com.naver.linewebtoon",
        "Referer": "https://m.webtoons.com/app/promotion/read/DiscordPhase2-Reading-December2024_Real_Fixed_NewCodes/progress?platform=APP_ANDROID",
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    
    cookies = {
        'wtu': token_urlsafe(24),
        'wtv': '1',
        'wts': str(int(time() * 1000)),
        'NEO_SES': neo_ses,
        'NEO_CHK': await get_chk(neo_ses, session),
        'locale': 'en',
        'needGDPR': 'false',
        'needCCPA': 'false',
        'needCOPPA': 'false',
        'inAppNeedGDPR': 'true',
        'inAppNeedCCPA': 'false',
        'inAppNeedCOPPA': 'false',
        'SDC': sdc,
        'cm_agr': 'false',
        'cm_ags': 'true',
        'countryCode': 'RO',
        'newlyAddedAndInitialized': 'nv',
        '__cmpconsentx47472': f"{token_urlsafe(2)}_{token_urlsafe(3)}_{token_urlsafe(25)}",
        '__cmpcccx47472': token_urlsafe(18),
    }

    try:
        response = await asyncio.to_thread(
            session.post,
            "https://m.webtoons.com/app/promotion/saveSubmitPayload",
            data=json.dumps(payload),
            headers=headers,
            cookies=cookies
        )
        try:
            result = response.json()
            if DEBUG:
                log.debug(f"Claim response: {result} Status: {response.status_code}")
            if result == True:
                return True
        except json.JSONDecodeError as e:
            log.failure(f"JSON decode error: {e}")
            
    except Exception as e:
        log.failure(f"Request error: {e}")
    
    return False

async def create_account(session, email=None, password=None, username=None):
    if password is None:
        password = await generate_password()
    if email is None:
        email = await generate_email()
        account_id, _ = await create_mail(email, password)
    if username is None:
        username = ''.join(random.choices(string.ascii_letters + string.digits, k=20))

    log.info(f"Creating account with email: {email}")
    cookies = getcookies()
    key = await get_key(session)
    headers = HeaderGenerator()() 
    
    headers.update({
        'Host': 'www.webtoons.com',
        'Origin': 'https://www.webtoons.com',
        'Referer': 'https://www.webtoons.com/member/join?loginType=EMAIL',
        'X-requested-with': 'XMLHttpRequest',
    })

    data = {
        'loginType': 'EMAIL',
        'nickname': username,
        'encnm': key['keyName'],
        'encpw': await encrypt(key, email, password),
        'zoneId': random.choice(pytz.all_timezones),
        'emailEventAlarm': 'true',
        'v': '3',
        'language': 'en',
        'year': str(random.randint(1980, 2005)),
        'month': str(random.randint(1, 12)),
        'dayOfMonth': str(random.randint(1, 28))
    }

    response = await asyncio.to_thread(
        session.post,
        'https://www.webtoons.com/member/join/doJoinById',
        cookies=cookies,
        headers=headers,
        data=data
    )

    if response.json()['success'] == True:
        log.success(f"Successfully created account for {email}")
        log.info(f"Verifying email...")
        token = MailTM().create_token(email, password)
        
        if token == 429:
            log.warning(f'Rate limited, waiting 5 seconds')
            await asyncio.sleep(5)
            token = MailTM().create_token(email, password)
 
        if DEBUG:
            log.debug(f"Credientials: {email}, {password}", )
            log.debug(f"Token: {token}")
        message_id = await get_email_message_id(token)
            
        verify_link = await get_verification_link(token, message_id)
        if verify_link and await verify_email(session, verify_link):
            log.success("Email verified successfully")
        
        with open("output/accounts.txt", 'a') as f:
            f.write(f"{email}:{password}\n")
        
                
        with open("output/full_account_capture.txt", 'a') as f:
            f.write(f"{username}:{email}:{password}:{token}\n")
        return email, password, account_id
    else:
        log.failure("Failed to create account, trying again...")
        return None, None, None

async def get_new_session():
    session = tls_client.Session(
        client_identifier="okhttp4_android_13",
        random_tls_extension_order=True,
        )

    try:
        with open("proxies.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
            session.proxies = proxies if proxies else []
    except FileNotFoundError:
        session.proxies = []
    return session

async def main():
    mail_client = MailMonitorClient()
    await mail_client.connect()
    try:
        while True:
            try:
                email, password, account_id = await create_account(session=await get_new_session())
                
                neo_ses = await get_neo(await get_new_session(), email, password)
                
                log.info("Reading episodes...")
                success, sdc = await read_all(await get_new_session(), neo_ses)
                
                if success and sdc:
                    log.info("Claiming promo...")
                    claimed = await claim(await get_new_session(), email, neo_ses, sdc)
                    if claimed:
                        log.success("Promo successfully claimed!")
                        log.info(f"Adding inbox {email} to monitoring queue")
                        token = MailTM().create_token(email, password)
                        response = await mail_client.add_inbox(email, token, account_id)
                        if DEBUG:
                            log.debug(f"Server response: {response['message']}")
                    else:
                        log.failure("Failed to claim promo, trying new account...")
                        continue
                else:
                    if success:
                        log.failure("Episodes read successfully but failed to get SDC cookie")
                    else:
                        log.failure("Failed to read episodes")
                    continue
            except Exception as e:
                log.failure(f"Error: {e}")
                continue
    
    except KeyboardInterrupt:
        log.info("Shutting down...")
    finally:
        await mail_client.close()

if __name__ == "__main__":
    asyncio.run(main())
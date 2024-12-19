import tls_client
from bs4 import BeautifulSoup
import time
from random_header_generator import HeaderGenerator

session = tls_client.Session(client_identifier="chrome_130", random_tls_extension_order=True)

def get_email_message_id(inbox_name, max_retries=3):
    for attempt in range(max_retries):
        response = session.get(f"https://mailnesia.com/mailbox/{inbox_name}")
        print(response.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        empty_box = soup.find('h2', class_='emails', string=lambda x: 'No e-mail message for' in str(x) if x else False)
        if empty_box:
            print(f"Empty mailbox, attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1: 
                time.sleep(1)
            continue
            
        email_rows = soup.find_all('tr', class_='emailheader')
        if not email_rows:
            print(f"No emails found, attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(1)
            continue
            
        for row in email_rows:
            subject = row.find('td', string=lambda text: text and '[WEBTOON] Verification Email' in text)
            if subject:
                return row.get('id')
        

        print(f"No verification email found, attempt {attempt + 1}/{max_retries}")
        if attempt < max_retries - 1:
            time.sleep(1)

    return None

def get_verification_link(inbox_name, email_id):
    response = session.get(f"https://mailnesia.com/mailbox/{inbox_name}/{email_id}?noheadernofooter=ajax")
    soup = BeautifulSoup(response.text, 'html.parser')
    verify_link = soup.find('a', href=lambda x: x and 'email-verification' in x)
    
    if verify_link:
        return verify_link['href']
    return None

def verify_email(verify_link):
    headers = HeaderGenerator()()
    headers.update({"Host": "www.webtoons.com",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",})


    verify_link = verify_link.replace("m.webtoons.com", "www.webtoons.com")
    verify_link = verify_link + "&webtoon-platform-redirect=true"
    print(verify_link)
    response = session.get(verify_link, headers=headers)
    print(response.headers)
    print(response.cookies)
    if response.status_code == 302 and "EMAIL_JOIN" in response.headers:
        return True
    elif response.status_code == 302 and "REQUEST_EXPIRED" in response.headers:
        print("Expired Link")
    return None

if __name__ == "__main__":
    email_id = get_email_message_id("oirzmxyxmnmiorrrosvzjolztp")
    print(f"Verification Email ID: {email_id}")
    if email_id:
        verify_link = get_verification_link("oirzmxyxmnmiorrrosvzjolztp", email_id)
        print(f"Verification Link: {verify_link}")
    
    if verify_link:
        if verify_email(verify_link):
            print("Verification Successful")
        else:
            print("Verification Failed")


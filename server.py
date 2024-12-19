import asyncio
import re
import json
from logmagix import Logger, Home
from mailtmwrapper import MailTM

class MailMonitor:
    def __init__(self):
        self.inbox_queue = asyncio.Queue()
        self.seen_entries = {}
        self.running_tasks = set()
        self.shutdown_event = asyncio.Event()
        self.clients = set()
        self.log = Logger()
        self.home = Home("Webtoon Server", "center", credits="discord.cyberious.xyz")
        self.home.display()

    async def fetch_inbox(self, token):
        try:
            messages = MailTM(token).get_messages()

            if messages == 429:
                self.log.warning("Warning, Rate limit exceeded, waiting 2 seconds")
                await asyncio.sleep(2)
                messages = MailTM(token).get_messages()

            if isinstance(messages, list):
                return messages
            return None
        except Exception as e:
            self.log.failure(f"Error fetching inbox: {e}")
            return None

    async def fetch_email_content(self, token, message_id):
        try:
            message = MailTM(token).get_message_by_id(message_id)
           
            if message:
                content = message.get('text', '')
                if not content and 'html' in message and message['html']:
                    content = message['html'][0]
                return content
            return None
        except Exception as e:
            self.log.failure(f"Error fetching email content: {e}")
            return None

    async def monitor_inbox(self, inbox_data):
        token = inbox_data.get('token')
        inbox_name = inbox_data.get('inbox_name')
        account_id = inbox_data.get('account_id')
        if not token:
            self.log.failure("No token provided for inbox monitoring")
            return

        self.log.info(f"Monitoring inbox {inbox_name}. ID: {account_id}")
        self.seen_entries[token] = set()

        while not self.shutdown_event.is_set():
            messages = await self.fetch_inbox(token)

            if messages:
                for message in messages:
                    message_id = message.get('id')
                    if message_id not in self.seen_entries[token]:
                        self.seen_entries[token].add(message_id)
                        email_content = await self.fetch_email_content(token, message_id)
                        if email_content:
                            promo_re = re.search(r"https:\/\/discord\.com\/billing\/promotions\/([A-Za-z0-9]+)", email_content)
                            if promo_re:
                                promo_link = promo_re.group(0)
                                with open("output/promos.txt", "a") as f:
                                    f.write(f"{promo_link}\n")
                                self.log.success(f"Promo link saved: {promo_link}")
                                try:
                                    MailTM(token).delete_account(account_id)
                                    self.log.success("Account deleted successfully")
                                except Exception as e:
                                    self.log.failure(f"Failed to delete account: {e}")
                                return
            else:
                self.log.warning(f"No messages found for inbox")

            await asyncio.sleep(60)

    async def monitor_from_queue(self):
        while not self.shutdown_event.is_set():
            inbox_data = await self.inbox_queue.get()
            if inbox_data.get('token') not in self.seen_entries:
                task = asyncio.create_task(self.monitor_inbox(inbox_data))
                self.running_tasks.add(task)
                task.add_done_callback(lambda t: self.running_tasks.discard(t))

    async def handle_client(self, reader, writer):
        self.clients.add(writer)
        try:
            while True:
                data = await reader.read(1024)
                if not data.strip():
                    break
                
                message = json.loads(data.decode())
                if message["action"] == "add_inbox":
                    await self.inbox_queue.put({
                        "token": message.get("token"),
                        "inbox_name": message.get("inbox_name"),
                        "account_id": message.get("account_id")
                    })
                    response = {"status": "success", "message": "Inbox added to monitoring queue"}
                    writer.write(json.dumps(response).encode())
                    await writer.drain()
                
        except Exception as e:
            self.log.failure(f"Client error: {e}")
        finally:
            self.clients.remove(writer)
            writer.close()
            await writer.wait_closed()

    async def start_server(self, host='127.0.0.1', port=8887):
        server = await asyncio.start_server(self.handle_client, host, port)
        self.log.info(f"Server running on {host}:{port}")
        
        monitor_task = asyncio.create_task(self.monitor_from_queue())
        
        try:
            async with server:
                await server.serve_forever()
        finally:
            self.shutdown_event.set()
            await asyncio.gather(*self.running_tasks, return_exceptions=True)
            monitor_task.cancel()

if __name__ == "__main__":
    mail_monitor = MailMonitor()
    asyncio.run(mail_monitor.start_server())

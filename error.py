import time
import os
import re
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env file

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f'Event type: {event.event_type}  path : {event.src_path}')
        if event.src_path == "/var/log/nginx/error.log":
            with open(event.src_path, "r") as file:
                last_two_lines = file.readlines()[-2:]
                for line in last_two_lines:
                    timestamp = re.search(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}', line)
                    host = re.search(r'host: "([^"]*)"', line)
                    if "HTTP/1.1\" 404" in line: 
                        print("Error 404 found!")
                        self.trigger_webhook('HTTP 404 error occurred in nginx', timestamp.group(), host.group(1) if host else 'Unknown')
                    elif "Unknown error" in line:
                        print("Unknown error found!")
                        self.trigger_webhook('Unknown error occurred in nginx', timestamp.group(), host.group(1) if host else 'Unknown')

    def trigger_webhook(self, error_msg, timestamp, host):
        url = os.getenv('WEBHOOK_URL')
        data = {'text': error_msg, 'timestamp': timestamp, 'host': host}
        response = requests.post(url, json=data)
        print("Webhook triggered, status code:", response.status_code)

if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path='/var/log/nginx/error.log', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

from dotenv import load_dotenv
import os
import re
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        with open(os.getenv('LOG_PATH'), 'r') as file:
            lines = file.readlines()
            for line in lines[-2:]:
                timestamp = re.search(r'(\w{3} \d{1,2} \d{2}:\d{2}:\d{2})', line)
                if 'HTTP/1.1" 400' in line or 'HTTP/1.1" 404' in line or 'Unknown error' in line:
                    host = re.search(r'host: "([^"]+)', line)
                    if timestamp is not None:
                        self.trigger_webhook('nginx error', timestamp.group(), host.group(1) if host else 'Unknown')
                elif 'unresponsive' in line and not '0 unresponsive' in line:
                    if timestamp is not None:
                        self.trigger_webhook('App became unresponsive', timestamp.group(), 'box.log')

    def trigger_webhook(self, error_msg, timestamp, host):
        url = os.getenv('WEBHOOK_URL')
        data = {'text': error_msg, 'timestamp': timestamp, 'host': host}
        response = requests.post(url, json=data)
        print("Webhook triggered, status code:", response.status_code)

if __name__ == "__main__":
    load_dotenv()
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.getenv('LOG_PATH'), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

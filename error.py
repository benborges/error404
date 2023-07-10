import time
import os
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f'Event type: {event.event_type}  path : {event.src_path}')
        if event.src_path == "/var/log/nginx/error.log":
            with open(event.src_path, "r") as file:
                lines = file.readlines()
                if "HTTP/1.1\" 404" in lines[-1]: # check if the last line of the file contains 'HTTP/1.1" 404'
                    print("Error 404 found!")
                    self.trigger_webhook()

    def trigger_webhook(self):
        url = 'https://your-webhook-url'
        data = {'text': 'HTTP 404 error occurred in nginx'}
        response = requests.post(url, json=data)
        print("Webhook triggered, status code:", response.status_code)

if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path='/var/log/nginx/', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

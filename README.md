# Python script to monitor my nginx error.log

This script watches /var/log/nginx/error.log for changes. Whenever the file is modified, it reads the last two lines. If a line contains 'HTTP/1.1" 404' or 'Unknown error', it sends a POST request to the webhook URL with a JSON object containing the error message, timestamp, and host. The webhook URL is loaded from a .env file.

## webhook

Using https://ntfy.sh to receive the errors and subscribe to them either on desktop or mobile
with the ability to tune notifications and only receive the ones that are urgent.

## usage

- cp .env-sample .env
- add your webhook url to send alerts to
- run python error.py

#!/usr/bin/python3

import os
import json
import time
import requests
import threading

from datetime import datetime
from urllib.parse import urlparse

urls = {}

if not os.path.isdir("data"):
    os.mkdir("data")

def update_configs():

    config = json.load(open("urls.json", encoding="utf-8"))

    for i in config.keys():
        if i not in urls.keys():
            print(f"[+] New url {i}")
            continue

        if urls[i] != config[i]:
            print(f"[+] Values for {i} has been updated to {config[i]}")

    return config

def poll_url(url, headers):

    try:
        r = requests.get(url, headers=headers, timeout=30)
        return r, r.text

    except requests.ConnectionError:
        print(f"[!] Connection error on connection to {url}!")
        return False


def thread_runner(url_config, url, flag):

    while True:

        target_files = []
        req_headers = {}
        ignore_headers = []
        wait = 2

        if flag.is_set():
            break

        if "request_headers" in url_config.keys():
            req_headers = url_config["request_headers"]

        if "seconds" in url_config.keys():
            wait = url_config["seconds"]

        if "ignore_headers" in url_config.keys():
            ignore_headers = url_config["ignore_headers"]

        packed_resp = poll_url(url, req_headers)

        if packed_resp is False:
            time.sleep(wait)
            continue

        resp, resp_content = packed_resp

        domain = urlparse(url).netloc

        for root, _,files in os.walk("data"):
            for fname in files:
                if not fname.endswith(".html"):
                    continue

                if fname.startswith(domain):
                    target_files.append(os.path.join(root, fname))
            
        resp_headers = dict(resp.headers)
        resp_status_code = int(resp.status_code)

        mutilated_headers = {}

        for k,v in resp_headers.items():
            if k in ignore_headers:
                continue

            mutilated_headers[k] = v

        have_match = False
        
        for i in target_files:

            html_content = open(i, encoding="utf-8").read()

            if html_content == resp_content:
                print(f"[+] Html response from {domain} matches with {i}")     
                have_match = True

            status = json.load(open(i.rsplit(".html", 1)[0]+".json", encoding="utf-8"))

            mutilated_status_headers = {}

            for k,v in status["resp_headers"].items():
                if k in ignore_headers:
                    continue

                mutilated_status_headers[k] = v

            if mutilated_status_headers == {"resp_headers": mutilated_headers, "status_code": resp_status_code}:
                print(f"[+] Response headers and status code from {domain} matches with {i}")
                have_match = True    

        if not have_match:
            print(f"[!] No matches with existing data with {domain}")

            timestamp = int((datetime.now() - datetime(1970, 1, 1)).total_seconds())
            open(f"data/{domain}_{timestamp}.html", "w", encoding="utf-8").write(resp_content)
            
            status = {"resp_headers": resp_headers, "status_code": resp_status_code}
            json.dump(status, open(f"data/{domain}_{timestamp}.json", "w", encoding="utf-8"))

        time.sleep(wait)

# 

threads = {}

while True:
    
    try:

        urls = update_configs()
        watch_urls = list(urls.keys())

        for k,v in threads.copy().items():
            
            if not k in watch_urls:
                print(f"[!] Stopped watching {k}")
                v[1].set()
                del threads[k]

        for i in watch_urls:
            if i in threads.keys():
                continue

            kill_flag = threading.Event()
            thread = threading.Thread(target = thread_runner, args=[urls[i], i, kill_flag])
            thread.start()

            threads.update({i:[thread, kill_flag]})

    except json.decoder.JSONDecodeError:
        # print("[!] Failed to decode json file")
        pass 
    
    except KeyboardInterrupt:
        print("[!] Exiting gracefully")

        for v in threads.copy().values():
            v[1].set()

        break
#!/bin/python3
#Author: avacadoPWN (Kovan MohammedAmeen)
#License: MIT

from time import sleep, time
import json
import queue
import ssl
import threading
import requests
import sys
import datetime
import os
from urllib3 import poolmanager
from concurrent.futures import ThreadPoolExecutor
from rich import print
t = datetime.datetime


if len(sys.argv) >= 2 and len(sys.argv) < 4:
    if len(sys.argv) == 2:
        args = {
            'urls_list': sys.argv[1],
            'json_export': None}
    else:
        args = {
            'urls_list': sys.argv[1],
            'json_export': sys.argv[2]}
else:
    print("Usage:\n\n" +
          "./headerz.py    url_list   stats_file(ndjson)\n")
    exit(-1)

print("\nNumber of Threads (default 65): ", end='')
num_of_threads = input()
if num_of_threads == '':
    num_of_threads = 65
elif not num_of_threads.isnumeric():
    print("[red]Error[/red], Thread amount must be in numeric value (0-250)\nTry again.")
    exit(-1)
else:
    num_of_threads = int(num_of_threads)


if args['json_export']:
    stats_file = args['json_export']
else:
    stats_file = args['urls_list'] + " - " + \
        t.now().strftime("%Y-%m-%d_%H-%M-%S") + ".ndjson"

results_directory = os.getcwd()

export_file = open(results_directory+stats_file, "a+")


try:
    urls = open(args['urls_list'], "r").read().splitlines()

except FileNotFoundError:
    print("\nError, URL list:", "'"+args['urls_list']+"'", "not found!")
    exit(-1)


q = queue.Queue()
for url in urls:
    q.put(url)


class EmptyURL(Exception):
    pass


class TLSAdapter(requests.adapters.HTTPAdapter):

    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLS,
            ssl_context=ctx)


thread_local = threading.local()


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
        thread_local.session.mount('https://', TLSAdapter())
    return thread_local.session


header = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}


def check(url):
    if url == '':
        print('empty url')
        raise EmptyURL
    session = get_session()

    try:
        if 'http' not in url:
            url = "https://"+url+"/"

        response = session.head(url, headers=header, timeout=10)
        add_to_dict(response.headers, url, response.url)
        stats['passed'] += 1
    except requests.exceptions.SSLError:
        stats['ssl_error'] += 1

    except EmptyURL:
        stats['num_of_requests'] += -1
        pass
    except Exception:
        stats['error'] += 1

    finally:
        stats['num_of_requests'] += 1
        print(stats['num_of_requests'], '/', stats['num_of_urls'], end='\r')


stats = {
    'num_of_requests': 0,
    'passed': 0,
    'ssl_error': 0,
    'error': 0,
    'num_of_urls': len(urls)
}


collected_data = {}


def add_to_dict(header, url, dest_url):
    collected_data[url] = {'url': dest_url, "headers": dict(header)}


counter = 0


def export_ndjson(data):
    global counter
    print('\nexporting the collected headers to NDJSON')
    for item in data:
        new_item = {}
        new_item['domain'] = item
        new_item['url'] = data[item]['url']
        new_item['headers'] = data[item]['headers']
        export_file.write(json.dumps(new_item))
        export_file.write('\n')
        counter += 1
        print("progress: {:d} /{:d}".format(counter, size), end='\r')


def main():
    with ThreadPoolExecutor(max_workers=num_of_threads) as executor:
        try:
            executor.map(check, [q.get() for x in range(q.qsize())])
        finally:
            executor.shutdown(wait=True)


t1 = time()
print('Fetching {} URLs...'.format(len(urls)))
main()
print()
print(stats)
size = len(collected_data)
export_ndjson(collected_data)
print("\n[green]All done.[/green]")
print("Time Elapsed: {:.2f} S\n".format(time()-t1))

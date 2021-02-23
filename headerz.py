#!/bin/python3
#Author: avacadoPWN (Kovan MohammedAmeen)
#License: MIT

import time,json,queue,ssl,threading,requests,sys,datetime
from urllib3 import poolmanager
from concurrent.futures import ThreadPoolExecutor
from rich import print
t = datetime.datetime
t1 = time.time()




if len(sys.argv) >= 2 and len(sys.argv) < 4:  
    if len(sys.argv) == 2: 
        args={
            'urls_list':sys.argv[1],
            'json_export': None}
    else:
        args={
            'urls_list':sys.argv[1],
            'json_export': sys.argv[2]}        
else:
    print("Usage:\n\n"+
          "./headerz.py    url_list   output_file\n")
    exit(-1)

print("\nNumber of Threads (default 65): ",end='')
num_of_threads= input() 
if num_of_threads == '':
    num_of_threads = 65
elif not num_of_threads.isnumeric():
    print("[red]Error[/red], Thread amount must be in numeric value (0-250)\nTry again.")
    exit(-1)
else:
    num_of_threads = int(num_of_threads)



if args['json_export']:
    output_file = args['json_export']
else:
    output_file = args['urls_list'] + " - " + t.now().strftime("%Y-%m-%d_%H-%M-%S")


export_file = open(output_file,"a")
failed_to_check = open("failed_"+output_file,"a")

try:
    urls  = open(args['urls_list'],"r").read()
except FileNotFoundError:
    print("\nError, URL list:","'"+args['urls_list']+"'","not found!")
    exit(-1)

urls = urls.splitlines()
q = queue.Queue()
for url in urls:
    q.put(url)


class TLSAdapter(requests.adapters.HTTPAdapter):

    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = poolmanager.PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                block=block,
                ssl_version=ssl.PROTOCOL_TLS,
                ssl_context=ctx)

session = requests.session()
session.mount('https://', TLSAdapter())
headers={'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0'}


output = {
    'current_url': '',
    'num_of_requests': 0,
    'passed':0,
    'ssl_error':0,
    'u_error':0,
    'num_of_urls': len(urls)
}

def failed_URL(url):
    failed_to_check.write(url+"\n")


def write_to_json(header,url,ssl=True):
    json_header={}
    json_header[url] = {'SSL':ssl,'headers':dict(header)}
    export_file.write(json.dumps(dict(json_header),indent=3, sort_keys=True) + '\n\n')



run_once= 0
def printer():
    global run_once
    global output

    if run_once == 0: 
        run_once= 1

        print(
            '\n'+
            'Fetching %d URLs...\n\n' %output['num_of_urls']+

            '++++++++++++++++++++++||| STATS |||+++++++++++++++++++++++\n\n'+

            'Requests_made:     200_OK:     SSL_Err:     Unk_Err:     '

        )
    else: 
        print(
            '{0}                 [light_green]{1}[/light_green]           [red]{2}            {3}[/red]   '.format(output['num_of_requests'], output['passed'], output['ssl_error'], output['u_error']),
            end='\r'
        )



class EmptyURL(Exception):
    pass




def check(url):
    if url == '': raise EmptyURL

    try:
        response= session.get("https://"+url+"/",headers=headers,timeout=15)    
        write_to_json(response.headers,url)
        output['passed'] += 1
    except requests.exceptions.SSLError:
        response= session.get("http://"+url+"/",headers=headers,timeout=15)
        write_to_json(response.headers,url,ssl=False)
        output['ssl_error'] += 1

    except KeyboardInterrupt:

        exit(-1)
    except EmptyURL:
        output['num_of_requests'] += -1
        pass
    except:
        #print(url,"Unknown Error")
        output['u_error'] += 1
        
    finally:
        output['num_of_requests'] += 1
        printer()



def main():
    try:
        with ThreadPoolExecutor(max_workers=num_of_threads) as executor:
            executor.map(check,[q.get() for x in range(q.qsize())])
            executor.shutdown(wait=True)
    except:
        pass

main()

export_file.close()
failed_to_check.close()


t2 = time.time()
print('\n')
print("[green]done![/green]")
print("Time Elapsed: {:.2f} S\n".format(t2-t1))







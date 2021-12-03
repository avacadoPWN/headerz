# headerz
is a light-weight https header collector based on python3

This tool was made as a part of a [research project](https://news.sophos.com/en-us/2021/11/22/the-state-of-world-wide-web-security-in-2021/).

## Features:

  * Multi-Threaded requests.

  * ND-JSON output.


## Requirements:
```bash
pip3 install -r requirements.txt
```
## Usage:
```bash
python3 headerz.py [url_list] [out_file]
```
## Note:

1. [out_file] argument is optional, if not specied it defaults to [url_list] + current date + time.

2. [url_list] must be a newline-delimited list.

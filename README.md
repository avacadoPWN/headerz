# headerz
is a light-weight https header collector based on python3

This tool was made as a part of a research project.

Features:

1- Multi-Threaded requests.

3- ND-JSON output.


Requirements:

      pip3 install -r requirements.txt

Usage:

      python3 headerz.py [url_list] [out_file]

Note:

1. [out_file] argument is optional, if not specied it defaults to [url_list] + current date + time.

2. [url_list] must be a newline-delimited list.

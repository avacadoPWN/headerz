# headerz
is a lightwight http/https header collector based on python3

At the moment the code is a bit of a mess but it gets the job done :) 
I will polish and add more features to it in the feature.

Features:

1- Multi-Threaded requests.

2- SSL check.

3- JSON output.


Requirements:

"pip3 install -r requirements.txt"

Usage:

"python3 headerz.py [url_list] [out_file]"

Note: [out_file] argument is optional, if not specied it defaults to [url_list] + current date + time.

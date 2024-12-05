# headerz
A modern, asynchronous HTTPS header collector written in Python 3

This tool was originally made as part of a [research project](https://news.sophos.com/en-us/2021/11/22/the-state-of-world-wide-web-security-in-2021/) and has been modernized with async support and improved features.

## Features

* Asynchronous requests using aiohttp for better performance
* Rich progress bars and status indicators
* ND-JSON output with header information
* Configurable concurrent connections and timeouts
* Modern CLI interface with help text and parameter validation
* Type-safe implementation using Pydantic
* Proper error handling and SSL support

## Requirements

```bash
pip install -r requirements.txt
```

## Usage

Basic usage:
```bash
python headerz.py urls.txt
```

Advanced usage with options:
```bash
python headerz.py urls.txt --json-export output.ndjson --num-threads 100 --timeout 15 --concurrent-limit 150
```

### Command Line Options

* `urls_list`: File containing list of URLs (required)
* `--json-export`: Output file for JSON results (optional)
* `--num-threads`: Number of concurrent threads (default: 65, range: 1-250)
* `--timeout`: Timeout in seconds for each request (default: 10)
* `--concurrent-limit`: Maximum number of concurrent connections (default: 100)

## Notes

1. The `json-export` argument is optional. If not specified, it defaults to `[url_list]-YYYY-MM-DD_HH-MM-SS.ndjson`
2. The URL list must be a newline-delimited file
3. The tool automatically handles both HTTP and HTTPS URLs
4. URLs without protocol specification default to HTTPS
5. Progress bars show real-time status of URL processing and export
6. Statistics are displayed after completion showing success/error counts

## Example Output

```json
{"domain": "example.com", "url": "https://example.com/", "headers": {"server": "nginx", "content-type": "text/html", ...}}
```

## Performance

The new async implementation offers significantly better performance compared to the thread-based version:
* Reduced memory usage
* Better handling of concurrent requests
* Faster processing of large URL lists
* Improved error recovery

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

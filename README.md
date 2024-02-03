# Web Watcher

Simple python script that polls a url and watches for any changes

# Usage

***Don't***

But if you really want to use it, copy `example_urls.json` to `urls.json` and edit it to your requirements

Here it is for convenience

```json
{
    "http://127.0.0.1:8000": {
        "seconds": 1,
        "ignore_headers": [
            "Date"
        ],
        "request_headers": {
            "User-Agent": "Web-Watcher"
        }
    }
}
```
`http://127.0.0.1:8000` is the url
`seconds` is the time to wait between each checks
`ignore_headers` is a list of headers to ignore in the checks
`requests_headers` is a dictionary of headers to send in checks

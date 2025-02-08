#!/usr/bin/env python3

import argparse
import httpx
import os
import re
from urllib.parse import urljoin, urlparse

def parse_input_file(input_file):
    """
    Parses BurpJSLinkFinder output to extract base URLs and endpoints.
    Returns a dictionary {base_url: [endpoints]}.
    """
    results = {}
    current_base_url = None

    with open(input_file, "r") as file:
        for line in file:
            line = line.strip()

            # Detect base URL from "[+] Valid URL found: ..."
            base_url_match = re.match(r"\[\+\] Valid URL found: (https?://[^\s]+)", line)
            if base_url_match:
                current_base_url = base_url_match.group(1)
                results[current_base_url] = []
                continue

            # Extract endpoints (lines starting with a number followed by "-")
            endpoint_match = re.match(r"\d+\s+-\s+(.+)", line)
            if endpoint_match and current_base_url:
                results[current_base_url].append(endpoint_match.group(1))

    return results

def construct_url(base_url, endpoint):
    """Constructs a full URL based on BurpJSLinkFinder output rules."""
    endpoint = endpoint.strip()

    # Parse base URL to extract JS directory
    parsed_url = urlparse(base_url)
    js_dir = os.path.dirname(parsed_url.path) + "/"

    # Full URLs (https://example.com/path)
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        return endpoint  

    # Absolute URLs or dotted URLs (/path or ../path)
    elif endpoint.startswith("/") or endpoint.startswith("../"):
        return urljoin(parsed_url.scheme + "://" + parsed_url.netloc, endpoint)

    # Relative URLs with at least one slash (text/test.php)
    elif "/" in endpoint:
        return urljoin(parsed_url.scheme + "://" + parsed_url.netloc + js_dir, endpoint)

    # Relative URLs without a slash (test.php)
    else:
        return urljoin(parsed_url.scheme + "://" + parsed_url.netloc + js_dir, endpoint)

def test_url(url):
    """Tests a URL using HTTPX and returns an HTTP status or detailed error."""
    try:
        response = httpx.get(url, follow_redirects=True, timeout=5, verify=False)
        return response.status_code  # Successfully retrieved a status code
    except httpx.HTTPStatusError as e:
        return f"HTTP Error {e.response.status_code}"
    except httpx.TimeoutException:
        return "Timeout"
    except httpx.ConnectError as e:
        return f"Connection Error ({e})"
    except httpx.RequestError as e:
        return f"Request Failed ({e})"

def main():
    parser = argparse.ArgumentParser(
        description="Parse BurpJSLinkFinder output, construct full URLs, and test them using HTTPX."
    )
    parser.add_argument("-i", "--input", required=True, help="Input file containing BurpJSLinkFinder output")
    parser.add_argument("-o", "--output", help="Output file to save results")

    args = parser.parse_args()

    parsed_data = parse_input_file(args.input)

    results = []
    for base_url, endpoints in parsed_data.items():
        print(f"\n[+] Processing URLs for base: {base_url}")

        for endpoint in endpoints:
            full_url = construct_url(base_url, endpoint)
            if full_url:
                status = test_url(full_url)
                result = f"[{status}] {full_url}"
                print(result)
                results.append(result)

    # Save results to output file if specified
    if args.output:
        with open(args.output, "w") as file:
            file.write("\n".join(results))
        print(f"\nResults saved to {args.output}")

if __name__ == "__main__":
    main()
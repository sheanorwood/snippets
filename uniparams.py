#!/usr/bin/env python3
# Author: Shea Norwood

# Description - this script removes duplicate urls and params from a list of urls

import urllib.parse
from collections import OrderedDict
import argparse
import sys

def normalize_url(url):
    """
    Normalize the URL by:
    - Parsing the URL into components.
    - Sorting the query parameters.
    - Assigning 'FUZZ' as the value for each parameter.
    - Reconstructing the normalized URL without the path for deduplication.
    """
    try:
        parsed = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)

        # Sort the parameters alphabetically by key
        sorted_params = sorted(query_params.items())

        # Assign 'FUZZ' to each parameter
        normalized_params = [(param, ['FUZZ']) for param, values in sorted_params]

        # Reconstruct the query string
        normalized_query = urllib.parse.urlencode(normalized_params, doseq=True)

        # Deduplication key: scheme + netloc + sorted normalized query
        dedup_key = urllib.parse.urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            '',  # Ignore the path
            '',  # Ignore params
            normalized_query,
            ''   # Ignore fragment
        ))

        # For output, reconstruct the URL with the original path and normalized query
        normalized_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            '',  # Ignore params
            normalized_query,
            ''   # Ignore fragment
        ))

        return dedup_key, normalized_url

    except Exception as e:
        print(f"Error processing URL: {url}\nException: {e}", file=sys.stderr)
        return None, None

def deduplicate_urls(input_file, output_file):
    """
    Read URLs from the input file, normalize them, deduplicate based on domain and params, and write to the output file.
    """
    unique_keys = {}
    total_urls = 0
    duplicate_urls = 0

    with open(input_file, 'r') as infile:
        for line in infile:
            url = line.strip()
            if not url:
                continue  # Skip empty lines

            total_urls += 1
            dedup_key, normalized_url = normalize_url(url)
            if dedup_key and normalized_url:
                if dedup_key not in unique_keys:
                    unique_keys[dedup_key] = normalized_url
                else:
                    duplicate_urls += 1

    with open(output_file, 'w') as outfile:
        for url in unique_keys.values():
            outfile.write(url + '\n')

    print(f"Deduplication complete.")
    print(f"Total URLs processed: {total_urls}")
    print(f"Unique URLs saved: {len(unique_keys)}")
    print(f"Duplicate URLs skipped: {duplicate_urls}")

def main():
    parser = argparse.ArgumentParser(
        description="""
Deduplicate and normalize URLs based on unique combinations of domain and query parameters.

This script processes a list of URLs, sets all query parameter values to 'FUZZ',
sorts the parameters, and retains only unique combinations based on domain and parameters,
ignoring the paths.

Usage:
    python3 uniparam.py -i input_urls.txt -o unique_urls.txt
""",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-i', '--input', required=True, help="Path to the input file containing URLs.")
    parser.add_argument('-o', '--output', required=True, help="Path to the output file to save unique URLs.")

    args = parser.parse_args()

    deduplicate_urls(args.input, args.output)

if __name__ == "__main__":
    main()
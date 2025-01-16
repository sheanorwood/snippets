#!/usr/bin/env python3
# Author: Shea Norwood
# Description: This script parses a Burp Suite JSON export to extract 'host' fields,
# cleans them by removing regex-specific characters and wildcards, prepends 'https://',
# removes duplicates, and saves the unique URLs to 'https.txt'.

import json
import re
import os

def extract_domain(host_pattern):
    """
    Extracts the base domain from the host pattern by removing regex characters and wildcards.
    
    Args:
        host_pattern (str): The host pattern string from the JSON data.
    
    Returns:
        str: The cleaned base domain.
    """
    # Remove regex-specific characters: ^, $, and escape characters \
    host = re.sub(r'[\\\^\$]', '', host_pattern)
    
    # Remove leading wildcard patterns like *., +., .*, .+., etc.
    host = re.sub(r'^(\.\*|\.\+|\*\.|\+\.)', '', host)
    
    # Remove any remaining wildcards within the domain (e.g., * or +)
    host = re.sub(r'[\*\+]', '', host)
    
    # Remove leading and trailing dots if any
    host = host.strip('.')
    
    return host

def get_input_filename():
    """
    Prompts the user to enter the input JSON filename.
    Validates the existence of the file.
    
    Returns:
        str: The valid input filename.
    """
    while True:
        filename = input("Enter the path to your Burp JSON file (e.g., burp_data.json): ").strip()
        if os.path.isfile(filename):
            return filename
        else:
            print(f"Error: The file '{filename}' does not exist. Please try again.\n")

def find_hosts(data, hosts=None, path=''):
    """
    Recursively searches for all 'host' or 'hostname' fields in the JSON data.
    
    Args:
        data (dict or list): The JSON data.
        hosts (list, optional): The list to accumulate host patterns.
        path (str, optional): The current JSON path (for debugging).
    
    Returns:
        list: A list of all found host patterns.
    """
    if hosts is None:
        hosts = []

    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            # Check for 'host' or 'hostname' (case-insensitive)
            if key.lower() in ['host', 'hostname']:
                print(f"Found '{key}' at path: {current_path} -> {value}")
                hosts.append(value)
            else:
                find_hosts(value, hosts, current_path)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            current_path = f"{path}[{index}]"
            find_hosts(item, hosts, current_path)

    return hosts

def main():
    # Configuration
    output_txt_file = 'https.txt'
    protocol = 'https://'  # Only prepend HTTPS

    # Prompt user for input file
    input_json_file = get_input_filename()

    try:
        # Read the JSON data
        with open(input_json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Find all 'host' or 'hostname' entries recursively
        host_patterns = find_hosts(data)

        if not host_patterns:
            print("\nNo 'host' or 'hostname' fields found in the JSON data.")
            print("Please verify the JSON structure or check for alternative key names.")
            return

        urls = set()  # Use a set to automatically handle duplicates

        for host_pattern in host_patterns:
            if host_pattern:
                domain = extract_domain(host_pattern)
                if domain:
                    full_url = protocol + domain
                    urls.add(full_url)
                    print(f"Processed URL: {full_url}")
                else:
                    print(f"Warning: Unable to extract domain from pattern '{host_pattern}'. Skipping.")
            else:
                print("Warning: Found an empty 'host' or 'hostname' field. Skipping.")

        if urls:
            # Write the unique URLs to the output file
            with open(output_txt_file, 'w', encoding='utf-8') as outfile:
                for url in sorted(urls):
                    outfile.write(url + '\n')

            print(f"\nSuccessfully written {len(urls)} unique URL(s) to '{output_txt_file}'.")
        else:
            print("No valid 'host' or 'hostname' entries found to process.")

    except json.JSONDecodeError:
        print(f"Error: The file '{input_json_file}' is not valid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
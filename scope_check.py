import re

def extract_domain(url):
    """Extract the domain from a given URL."""
    match = re.search(r'^(?:https?://)?(?:www\.)?([^/:]+)', url)
    return match.group(1) if match else None

def read_domains_from_file(filename):
    """
    Read lines from a file and strip schemes (http/https) and trailing slashes.
    Return a list of bare domain strings like 'example.com'.
    """
    domains = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Remove 'http://' or 'https://' if present
            line = re.sub(r'^https?://', '', line)
            # Remove trailing slash if any
            line = line.rstrip('/')
            # Also remove a leading 'www.' if you don't want to store it
            # (This is optional, depending on your needs)
            line = re.sub(r'^www\.', '', line)
            domains.append(line)
    return domains

def domain_in_scope(domain, scope_domain, allow_wildcards):
    """
    Check if 'domain' is in scope based on 'scope_domain' and wildcard preference.
    
    If allow_wildcards=True, then any subdomain of 'scope_domain' matches.
    For example, 'scope_domain' = 'example.com', domain_in_scope('sub.example.com', scope_domain, True) => True.
    Otherwise, exact or www. match only.
    """
    if allow_wildcards:
        # e.g. scope_domain = 'example.com'
        # any domain that ends with 'example.com' (and is not exactly 'example.com' if you want subdomains)
      
        return domain == scope_domain or domain.endswith(f".{scope_domain}")
    else:
        # Exact match or 'www.' variants
        return (domain == scope_domain or
                domain == f"www.{scope_domain}" or
                f"www.{domain}" == scope_domain)

def is_in_scope(domain, scope_domains, allow_wildcards):
    """
    Loop over all scope_domains and see if 'domain' is in any of them based on wildcard preference.
    """
    for scope_d in scope_domains:
        if domain_in_scope(domain, scope_d, allow_wildcards):
            return True
    return False

def process_urls(scope_file, url_file):
    """Process URLs, classify them as in-scope or out-of-scope, and handle results."""

    #  Ask if the user wants wildcard subdomains
    allow_wildcards_str = input("Do you want to allow wildcard subdomains? (yes/no): ").strip().lower()
    allow_wildcards = (allow_wildcards_str == "yes")

    #  Ask if there is an out-of-scope file
    has_oos_file = input("Are there any out-of-scope URLs? (yes/no): ").strip().lower()

    out_of_scope_list = []
    if has_oos_file == "yes":
        oos_filename = input("Enter the out-of-scope file name: ").strip()
        out_of_scope_list = read_domains_from_file(oos_filename)

    #  Read scope domains from the scope file
    scope_domains = read_domains_from_file(scope_file)

    #  Read URLs from the URL file
    with open(url_file, 'r') as uf:
        urls = [line.strip() for line in uf if line.strip()]

    in_scope_urls = []
    out_of_scope_urls = []

    # Classify URLs
    for url in urls:
        domain = extract_domain(url)

        if not domain:
            # If domain cannot be parsed, default to out of scope
            out_of_scope_urls.append(url)
            continue

        # Check if domain is in out-of-scope list
  
        if any(d == domain or domain.endswith(f".{d}") for d in out_of_scope_list):
            out_of_scope_urls.append(url)
            continue

        # Now check if domain is in scope
        if is_in_scope(domain, scope_domains, allow_wildcards):
            in_scope_urls.append(url)
        else:
            out_of_scope_urls.append(url)

    # Output results
    print("\nIn-scope URLs:")
    print("\n".join(in_scope_urls))

    print("\nOut-of-scope URLs:")
    print("\n".join(out_of_scope_urls))

    # Optional saving of results
    save_cleaned = input("\nDo you want to save in-scope URLs? (yes/no): ").strip().lower()
    if save_cleaned == "yes":
        cleaned_file = input("Enter the filename to save in-scope URLs: ").strip()
        with open(cleaned_file, 'w') as cf:
            cf.write("\n".join(in_scope_urls))
        print(f"In-scope URLs saved to {cleaned_file}")

    save_removed = input("\nDo you want to save out-of-scope URLs? (yes/no): ").strip().lower()
    if save_removed == "yes":
        removed_file = input("Enter the filename to save out-of-scope URLs: ").strip()
        with open(removed_file, 'w') as rf:
            rf.write("\n".join(out_of_scope_urls))
        print(f"Out-of-scope URLs saved to {removed_file}")

if __name__ == "__main__":
    scope_file = input("Enter the scope file name: ").strip()
    url_file = input("Enter the URL file name: ").strip()
    process_urls(scope_file, url_file)
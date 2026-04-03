import os
import json
import subprocess
import shutil
import sys
import platform
import argparse
import threading
import time
from datetime import datetime
from colorama import Fore, Style, init as colorama_init

colorama_init()


def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()

parser = argparse.ArgumentParser(description="PyHttrack - Website Downloader")
parser.add_argument("--url", help="Single URL to download (overrides web.json)")
args = parser.parse_args()


def format_size(bytes_num):
    try:
        bytes_num = int(bytes_num)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_num < 1024:
                return f"{bytes_num:.2f} {unit}"
            bytes_num /= 1024
        return f"{bytes_num:.2f} PB"
    except:
        return "-"


arch = platform.machine().lower()
system = platform.system().lower()

arch_map = {
    "x86_64": "x64",
    "amd64": "x64",
    "i386": "x86",
    "i686": "x86",
    "arm64": "arm64",
    "aarch64": "arm64",
}

folder_arch = arch_map.get(arch)
wget_filename = "wget.exe" if system == "windows" else "wget"
wget_path = (
    os.path.join(BASE_DIR, "wget", folder_arch, wget_filename) if folder_arch else None
)


def install_wget():
    if system == "linux":
        print("Wget not found. Trying to install wget...")
        try:
            subprocess.run(["apt", "update"], check=True)
            subprocess.run(["apt", "install", "-y", "wget"], check=True)
            print("Wget installed successfully.")
            return shutil.which("wget")
        except subprocess.CalledProcessError:
            print("Failed to install wget. Make sure you have sudo access.")
    else:
        print("Automatic installation only supported on Linux.")
    return None


def print_banner():
    print(f"""
{Fore.RED}
:::====  ::: === :::  === :::==== :::==== :::====  :::====  :::===== :::  ===
:::  === ::: === :::  === :::==== :::==== :::  === :::  === :::      ::: === 
=======   =====  ========   ===     ===   =======  ======== ===      ======  {Fore.WHITE}
===        ===   ===  ===   ===     ===   === ===  ===  === ===      === === 
===        ===   ===  ===   ===     ===   ===  === ===  ===  ======= ===  ===
                                                                            
{Style.RESET_ALL}
""")


if wget_path and os.path.isfile(wget_path):
    if system != "windows":
        os.chmod(wget_path, 0o755)
    wget_exec = wget_path
elif shutil.which("wget"):
    wget_exec = "wget"
else:
    wget_exec = install_wget()
    if not wget_exec:
        print("Cannot find or install wget.")
        sys.exit(1)

os.system("cls" if os.name == "nt" else "clear")

results = []
urls = []

web_dir = (
    os.path.join(os.path.expanduser("~"), "pyhttrack")
    if system == "linux"
    else os.getcwd()
)
os.makedirs(web_dir, exist_ok=True)

try:
    web_json_path = (
        os.path.join(os.path.expanduser("~"), "pyhttrack", "web.json")
        if system == "linux"
        else os.path.join(BASE_DIR, "web.json")
    )
    with open(web_json_path, "r") as file:
        urls = json.load(file)
except FileNotFoundError:
    print("File 'web.json' not found.")

if args.url:
    urls = [args.url]

print_banner()

spinner_active = False
spinner_stop_event = threading.Event()


def spin():
    chars = "|/-\\"
    idx = 0
    while not spinner_stop_event.is_set():
        sys.stdout.write(
            f"\r{Fore.CYAN}Downloading... {chars[idx % len(chars)]}{Style.RESET_ALL}"
        )
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    sys.stdout.flush()


def start_spinner():
    global spinner_active
    spinner_active = True
    spinner_stop_event.clear()
    threading.Thread(target=spin, daemon=True).start()


def stop_spinner():
    global spinner_active
    spinner_active = False
    spinner_stop_event.set()


if not urls:
    print("No URLs found in 'web.json'.")
    urls.append(input("Enter URL: "))

print(f"\nTotal URL : {len(urls)}")
print("==================\n")

for url in urls:
    print(f"Downloading: {url}\n")
    url_has_result = False
    start_spinner()

    try:
        process = subprocess.Popen(
            [
                wget_exec,
                "-r",
                "-m",
                "--no-parent",
                "--convert-links",
                "--adjust-extension",
                "--page-requisites",
                "--limit-rate=100k",
                "--random-wait",
                "--wait=1",
                "--timeout=15",
                "--tries=3",
                "--no-check-certificate",
                "--retry-connrefused",
                "-e",
                "robots=off",
                "--user-agent=Mozilla/5.0",
                "--directory-prefix",
                web_dir,
                url,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        for line in process.stdout:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            line = line.strip()

            if "Saving" in line and "/" in line:
                try:
                    path = (
                        line.split("'")[1]
                        if "'" in line
                        else line.split("Saving ")[-1].strip()
                    )
                    size = "-"
                    results.append(
                        {
                            "timestamp": now,
                            "url": url,
                            "file": path,
                            "status": "success",
                            "size": size,
                        }
                    )
                    print(f"{Fore.GREEN}[{now}] Downloaded:{Style.RESET_ALL} {path}")
                    url_has_result = True
                except:
                    continue

            elif "HTTP response 304" in line:
                try:
                    results.append(
                        {
                            "timestamp": now,
                            "url": url,
                            "file": "-",
                            "status": "success",
                            "size": "-",
                        }
                    )
                    print(
                        f"{Fore.YELLOW}[{now}] Already up to date:{Style.RESET_ALL} {url}"
                    )
                    url_has_result = True
                except:
                    continue

            elif "convert" in line.lower() and "http" not in line.lower():
                try:
                    results.append(
                        {
                            "timestamp": now,
                            "url": url,
                            "file": "-",
                            "status": "success",
                            "size": "-",
                        }
                    )
                    print(
                        f"{Fore.GREEN}[{now}] Download Complete:{Style.RESET_ALL} {url}"
                    )
                    url_has_result = True
                except:
                    continue

            elif "not modified" in line and "'" in line:
                try:
                    path = (
                        line.split("'")[1]
                        if "'" in line
                        else line.split("Saving ")[-1].strip()
                    )
                    size = "-"
                    results.append(
                        {
                            "timestamp": now,
                            "url": url,
                            "file": path,
                            "status": "success",
                            "size": size,
                        }
                    )
                    print(f"{Fore.GREEN}[{now}] Downloaded:{Style.RESET_ALL} {path}")
                    url_has_result = True
                except:
                    continue

            elif "not modified" in line and "'" in line:
                try:
                    path = line.split("'")[1]
                    results.append(
                        {
                            "timestamp": now,
                            "url": url,
                            "file": path,
                            "status": "not modified",
                            "size": "-",
                        }
                    )
                    print(f"{Fore.YELLOW}[{now}] Skipped:{Style.RESET_ALL} {path}")
                    url_has_result = True
                except:
                    continue

        process.wait()

        if not url_has_result:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{Fore.RED}Failed to Download:{Style.RESET_ALL} {url}")
            results.append(
                {
                    "timestamp": now,
                    "url": url,
                    "file": "-",
                    "status": "failed",
                    "size": "-",
                }
            )

    except Exception as e:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Fore.RED}Error while downloading:{Style.RESET_ALL} {url} | {str(e)}")
        results.append(
            {"timestamp": now, "url": url, "file": "-", "status": "failed", "size": "-"}
        )
    finally:
        stop_spinner()

if results:
    base_dir_for_log = (
        os.path.join(os.path.expanduser("~"), "pyhttrack")
        if system == "linux"
        else BASE_DIR
    )
    log_path = os.path.join(base_dir_for_log, "log.txt")
    with open(log_path, "a", encoding="utf-8") as log_file:
        for result in results:
            log_file.write(
                f"[{result['timestamp']}] {result['url']} | {result['file']} | {result['status']} | {result['size']}\n"
            )
else:
    print("No URLs to process.")
    sys.exit(0)

success = sum(r["status"] == "success" for r in results)
skipped = sum(r["status"] == "not modified" for r in results)
failed = sum(
    r["status"] in ["failed", "404 not found", "403 forbidden"] for r in results
)

print(f"\n{Fore.GREEN}Success : {success}{Style.RESET_ALL}")
print(f"{Fore.YELLOW}Skipped : {skipped}{Style.RESET_ALL}")
print(f"{Fore.RED}Failed  : {failed}{Style.RESET_ALL}")

output_base = (
    os.path.join(os.path.expanduser("~"), "pyhttrack")
    if system == "linux"
    else os.getcwd()
)

if results:
    print(f"\n{Fore.CYAN}Output  :{Style.RESET_ALL}")
    for r in results:
        if r["status"] == "success":
            if r["file"] != "-":
                folder = r["file"].split("/")[0] if "/" in r["file"] else r["file"]
            else:
                from urllib.parse import urlparse

                folder = urlparse(r["url"]).netloc
            print(f"  {output_base}/{folder}")

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
from urllib.parse import urlparse

colorama_init()

VERSION = "1.0.0.patch-006"

def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()

parser = argparse.ArgumentParser(description="PyHttrack - Website Downloader")
parser.add_argument("--url", help="Single URL to download (overrides web.json)")
args = parser.parse_args()

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
                                                                            
v{VERSION}
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

try:
    web_json_path = (
        os.path.join(os.path.expanduser("~"), "pyhttrack", "web.json")
        if system == "linux"
        else os.path.join(BASE_DIR, "web.json")
    )
    with open(web_json_path, "r") as file:
        urls = json.load(file)
except FileNotFoundError:
    pass

if args.url:
    urls = [args.url]

print_banner()

spinner_active = False
spinner_stop_event = threading.Event()

def spin():
    chars = "|/-\\"
    idx = 0
    while not spinner_stop_event.is_set():
        sys.stdout.write(f"\r{Fore.CYAN}Downloading... {chars[idx % len(chars)]}{Style.RESET_ALL}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    # Hapus teks spinner pas selesai biar output gak numpuk
    sys.stdout.write("\r" + " " * 30 + "\r")
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
    urls.append(input("Enter URL: "))

print(f"\nTotal URL : {len(urls)}")
print("==================\n")

env = os.environ.copy()
env["LC_ALL"] = "C"
env["LANG"] = "C"

for url in urls:
    print(f"Target: {url}")
    url_has_result = False
    start_spinner()
    domain = urlparse(url).netloc
    web_dir = os.path.join(os.getcwd(), domain)
    os.makedirs(web_dir, exist_ok=True)

    try:
        process = subprocess.Popen(
            [
                wget_exec,
                "-r",
                "-m",
                "-p",
                "-k",
                "-E",
                "-nH",
                "--restrict-file-names=windows",
                "--accept",
                "css,html,html,js,jpg,jpeg,png,gif,svg,ico,webp,bmp,tiff",
                "--tries=3",
                "--no-check-certificate",
                "--retry-connrefused",
                "-e",
                "robots=off",
                "--execute",
                "robots=off",
                "--user-agent=Mozilla/5.0",
                "--directory-prefix",
                web_dir,
                url,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env
        )

        for line in process.stdout:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            line = line.strip()

            if "Saving" in line or "Menyimpan" in line:
                try:
                    if "'" in line:
                        path = line.split("'")[1]
                    elif "‘" in line and "’" in line:
                        path = line.split("‘")[1].split("’")[0]
                    else:
                        path = line.split(" ")[-1].strip().strip("'").strip('"')

                    if os.path.isabs(path):
                        path = os.path.relpath(path, web_dir)

                    results.append({"timestamp": now, "url": url, "file": path, "status": "success", "size": "-"})
                    print(f"\r{Fore.GREEN}[{now}] Downloaded:{Style.RESET_ALL} {path}" + " "*10)
                    url_has_result = True
                except:
                    continue

            elif "HTTP response 304" in line:
                results.append({"timestamp": now, "url": url, "file": "-", "status": "success", "size": "-"})
                print(f"\r{Fore.YELLOW}[{now}] Already up to date:{Style.RESET_ALL} {url}" + " "*10)
                url_has_result = True

            elif "Downloaded:" in line and "files" in line:
                url_has_result = True

            elif line.startswith("convert ") or ("convert" in line.lower() and "http" in line.lower()):
                url_has_result = True

            elif "not modified" in line and ("'" in line or "‘" in line):
                try:
                    if "'" in line:
                        path = line.split("'")[1]
                    elif "‘" in line and "’" in line:
                        path = line.split("‘")[1].split("’")[0]
                    else:
                        path = line.split(" ")[-1].strip().strip("'").strip('"')

                    if os.path.isabs(path):
                        path = os.path.relpath(path, web_dir)

                    results.append({"timestamp": now, "url": url, "file": path, "status": "not modified", "size": "-"})
                    print(f"\r{Fore.YELLOW}[{now}] Skipped:{Style.RESET_ALL} {path}" + " "*10)
                    url_has_result = True
                except:
                    continue

        process.wait()

        # Kalau bener-bener gak ada log sukses/gagal dari Wget
        if not url_has_result:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\r{Fore.RED}Failed to Download:{Style.RESET_ALL} {url}" + " "*20)
            results.append({"timestamp": now, "url": url, "file": "-", "status": "failed", "size": "-"})
        else:
            # Kalau sukses jalan tapi list results untuk URL ini masih kosong (berarti gak ada file baru/udah ke-cache)
            if not any(r["url"] == url for r in results):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\r{Fore.YELLOW}[{now}] Checked (Already up to date / No new files):{Style.RESET_ALL} {url}" + " "*10)
                results.append({"timestamp": now, "url": url, "file": "No new files", "status": "success", "size": "-"})

    except Exception as e:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\r{Fore.RED}Error while downloading:{Style.RESET_ALL} {url} | {str(e)}" + " "*20)
        results.append({"timestamp": now, "url": url, "file": "-", "status": "failed", "size": "-"})
    finally:
        stop_spinner()

if results:
    base_dir_for_log = os.getcwd()
    log_path = os.path.join(base_dir_for_log, "log.txt")
    with open(log_path, "a", encoding="utf-8") as log_file:
        for result in results:
            log_file.write(f"[{result['timestamp']}] {result['url']} | {result['file']} | {result['status']} | {result['size']}\n")
else:
    print("\nNo URLs to process.")
    sys.exit(0)

success = sum(r["status"] == "success" for r in results)
skipped = sum(r["status"] == "not modified" for r in results)
failed = sum(r["status"] in ["failed", "404 not found", "403 forbidden"] for r in results)

print(f"\n{Fore.GREEN}Success : {success}{Style.RESET_ALL}")
print(f"{Fore.YELLOW}Skipped : {skipped}{Style.RESET_ALL}")
print(f"{Fore.RED}Failed  : {failed}{Style.RESET_ALL}")

output_base = os.getcwd()

print(f"\n{Fore.CYAN}Output  :{Style.RESET_ALL}")
saved_files = []
for r in results:
    if r["status"] in ["success", "not modified"] and r["file"] not in ["-", "No new files"]:
        if r["file"].startswith(web_dir):
            rel_path = os.path.relpath(r["file"], web_dir)
            saved_files.append(rel_path)
        else:
            saved_files.append(r["file"])

if saved_files:
    print(f"  ./")
    for file in saved_files[:8]:
        print(f"    {file}")
    if len(saved_files) > 8:
        print(f"    ... and {len(saved_files) - 8} more files")
else:
    print("  (Semua resource sudah ter-download/up-to-date)")

print(f"\n  All files saved in: {output_base}/")
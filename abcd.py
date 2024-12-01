import requests
import json
import random
import time
import os
from colorama import Fore, Style, init
import urllib3
import asyncio
import socks
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

init()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Colors:
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    WHITE = Fore.WHITE
    RESET = Style.RESET_ALL

banner = """
               ╔═╗╔═╦╗─╔╦═══╦═══╦═══╦═══╗
               ╚╗╚╝╔╣║─║║╔══╣╔═╗║╔═╗║╔═╗║
               ─╚╗╔╝║║─║║╚══╣║─╚╣║─║║║─║║
               ─╔╝╚╗║║─║║╔══╣║╔═╣╚═╝║║─║║
               ╔╝╔╗╚╣╚═╝║╚══╣╚╩═║╔═╗║╚═╝║
               ╚═╝╚═╩═══╩═══╩═══╩╝─╚╩═══╝
               My GitHub: github.com/Gzgod
               My Twitter: Twitter Snow God @Hy78516012                   """

def logger(message, level='info', value=""):
    now = time.strftime('%Y-%m-%dT%H:%M:%S')
    colors = {
        'info': Colors.GREEN,
        'warn': Colors.YELLOW,
        'error': Colors.RED,
        'success': Colors.BLUE,
        'debug': Colors.WHITE,
    }
    color = colors.get(level, Colors.WHITE)
    print(f"{color}[{now}] [{level.upper()}]: {message}{Colors.RESET}", f"{Colors.YELLOW}{value}{Colors.RESET}")

def ask_question(query):
    return input(query)

def get_random_quality():
    return random.randint(60, 99)

def get_proxies():
    if not os.path.exists('proxy.txt'):
        logger("Proxy file proxy.txt not found!", 'error')
        return []
    with open('proxy.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

def get_tokens():
    if not os.path.exists('token.txt'):
        logger("Token file token.txt not found!", 'error')
        return []
    with open('token.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

class SOCKS5Adapter(HTTPAdapter):
    def __init__(self, socks_proxy=None, **kwargs):
        self.socks_proxy = socks_proxy
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['proxy'] = self.socks_proxy
        kwargs['proxy_kwargs'] = {'proxy_type': socks.SOCKS5, 'address': self.socks_proxy}
        return super().init_poolmanager(*args, **kwargs)

async def share_bandwidth(token, proxy=None):
    try:
        quality = get_random_quality()

        if proxy:
            proxies = {
                'http': f'socks5://{proxy}',
                'https': f'socks5://{proxy}'
            }
            session = requests.Session()
            session.mount('http://', SOCKS5Adapter(socks_proxy=proxy))
            session.mount('https://', SOCKS5Adapter(socks_proxy=proxy))
            response = session.post('https://api.openloop.so/bandwidth/share',
                                    headers={'Authorization': f'Bearer {token}',
                                             'Content-Type': 'application/json'},
                                    json={'quality': quality},
                                    proxies=proxies,
                                    verify=False)
        else:
            response = requests.post('https://api.openloop.so/bandwidth/share',
                                     headers={'Authorization': f'Bearer {token}',
                                              'Content-Type': 'application/json'},
                                     json={'quality': quality},
                                     verify=False)

        response.raise_for_status()
        data = response.json()

        if 'data' in data and 'balances' in data['data']:
            balance = data['data']['balances'].get('POINT', 'N/A')
            logger(f"Bandwidth sharing successful Info: {Colors.YELLOW}{data.get('message', 'No message')}{Colors.RESET} | "
                   f"Score: {Colors.YELLOW}{quality}{Colors.RESET} | "
                   f"Total earnings: {Colors.YELLOW}{balance}{Colors.RESET}")
        else:
            logger(f"Unexpected response format: {data}", 'warning')

    except requests.RequestException as e:
        logger(f"Error while sharing bandwidth with proxy {proxy}: {e}", 'error')
        return False  # Indicate failure for this proxy
    return True  # Indicate success for this proxy

async def share_bandwidth_for_all_tokens(proxies=None):
    tokens = get_tokens()
    active_proxies = proxies or []  # If no proxies, use an empty list
    for index, token in enumerate(tokens):
        proxy = active_proxies[index] if index < len(active_proxies) else None
        logger(f"Sharing bandwidth for account {index + 1}...", 'info')
        
        success = await share_bandwidth(token, proxy)
        
        # If the proxy fails, remove it
        if not success and proxy:
            logger(f"Removing dead proxy: {proxy}", 'warn')
            active_proxies.remove(proxy)
            if not active_proxies:  # If all proxies are removed, stop the process
                logger("All proxies have failed. Exiting...", 'error')
                break

# Other functions remain the same...

def main_menu():
    while True:
        print(Colors.MAGENTA + banner + Colors.RESET)
        print(f"{Colors.YELLOW}1. Start Node")
        print(f"2. Register or Get Token")
        print(f"3. Exit")
        choice = ask_question(f"{Colors.WHITE}Choose (1, 2, or 3): {Colors.RESET}")

        if choice == '1':
            use_proxy_choice = ask_question('Use proxy to start node? (y/n): ').lower()
            proxies = get_proxies() if use_proxy_choice == 'y' else None
            if use_proxy_choice == 'y' and not proxies:
                logger("No proxies available, proceeding without proxy.", 'warn')

            logger('Starting bandwidth sharing...')
            loop = asyncio.get_event_loop()
            loop.run_until_complete(share_bandwidth_for_all_tokens(proxies))

            while True:
                time.sleep(60)
                loop.run_until_complete(share_bandwidth_for_all_tokens(proxies))

        elif choice == '2':
            register_user()
        elif choice == '3':
            logger('Exiting application...')
            break
        else:
            logger('Invalid option, please try again.', 'warn')

if __name__ == "__main__":
    main_menu()

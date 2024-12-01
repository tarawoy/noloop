import requests
import json
import random
import time
import os
from colorama import Fore, Style, init
import urllib3
import asyncio

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

async def share_bandwidth(token, proxy=None):
    try:
        quality = get_random_quality()
        proxies = {'https': f'http://{proxy}'} if proxy else None

        response = requests.post('https://api.openloop.so/bandwidth/share',
                                 headers={'Authorization': f'Bearer {token}',
                                          'Content-Type': 'application/json'},
                                 json={'quality': quality},
                                 proxies=proxies,
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
        logger(f"Error while sharing bandwidth: {e}", 'error')

async def share_bandwidth_for_all_tokens(proxies=None):
    tokens = get_tokens()
    for index, token in enumerate(tokens):
        proxy = proxies[index] if proxies and index < len(proxies) else None
        logger(f"Sharing bandwidth for account {index + 1}...", 'info')
        await share_bandwidth(token, proxy)

def get_account_info():
    if not os.path.exists('accounts.txt'):
        logger("Account information file accounts.txt not found!", 'error')
        return []
    with open('accounts.txt', 'r') as file:
        return [line.strip().split(',') for line in file if line.strip()]

def login_user(email, password, use_proxy=True):
    try:
        login_payload = {'username': email, 'password': password}
        proxies = None if not use_proxy else {'https': f'http://{get_proxies()[0]}'}

        login_response = requests.post('https://api.openloop.so/users/login',
                                       headers={'Content-Type': 'application/json'},
                                       data=json.dumps(login_payload),
                                       proxies=proxies,
                                       verify=False)

        if login_response.status_code != 200:
            raise requests.HTTPError(f"Login failed, status code: {login_response.status_code}")

        login_data = login_response.json()
        access_token = login_data.get('data', {}).get('accessToken', '')
        if access_token:
            logger('Login successful, obtained Token:', 'success', access_token)
            with open('token.txt', 'a') as token_file:
                token_file.write(f"{access_token}\n")
            logger('Access token saved to token.txt')
        else:
            logger('Failed to extract access token from login response.', 'error')
    except requests.RequestException as e:
        logger('Error during login process:', 'error', e)

def register_user():
    try:
        accounts = get_account_info()
        if not accounts:
            logger("Account information file accounts.txt is empty!", 'error')
            return

        use_proxy_choice = ask_question('Use proxy for registration? (y/n): ').lower()
        invite_code = ask_question('Enter your invite code (all accounts will use this invite code): ')

        for email, password in accounts:
            registration_payload = {'name': email, 'username': email, 'password': password, 'inviteCode': invite_code}
            proxies = {'https': f'http://{get_proxies()[0]}'} if use_proxy_choice == 'y' else None

            try:
                register_response = requests.post('https://api.openloop.so/users/register',
                                                  headers={'Content-Type': 'application/json'},
                                                  data=json.dumps(registration_payload),
                                                  proxies=proxies,
                                                  verify=False)

                if register_response.status_code == 401:
                    logger(f'Email {email} already exists. Attempting login...')
                    login_user(email, password, use_proxy_choice == 'y')
                elif register_response.status_code == 200:
                    logger(f'Registration for {email} successful:', 'success')
                    login_user(email, password, use_proxy_choice == 'y')
                else:
                    raise requests.HTTPError(f"Registration for {email} failed, status code: {register_response.status_code}")
            except requests.RequestException as e:
                logger(f'Error during registration or login for {email}:', 'error', e)

    except KeyboardInterrupt:
        logger('Process interrupted by user.', 'info')

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

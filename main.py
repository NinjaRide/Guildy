import threading
import os
import tls_client
import random
import colorama
from colorama import Fore
import yaml
from pystyle import *
import time
import re


def cpm_counter():
    while True:
        previous = data['checked']
        time.sleep(1)
        after = data['checked']
        data['cpm'] = (after-previous) * 60

def update_title():
    os.system(
        f"""title GUILDY By NinjaRide - Checked: [{data['checked']}] - Left: [{len(tokens)}] - GOOD: [{data['valid']}] - BAD: [{data["invalid"]}] - UHQ: [{data['uhq']}]- MQ: [{data['mq']}] - LQ: [{data['lq']}]- Guilds: [{data['guilds']}]- CPM: [{data['cpm']}] """
    )
    threading.Timer(.1,update_title).start()  

def tprint(text: str):
    with locker:
        print(text)


data = {
            'valid': 0,
            'invalid': 0,
            'checked': 0,
            'retries': 0,
            'cpm': 0,
            'guilds': 0,
            'uhq': 0,
            'mq': 0,
            'lq': 0

        }




def logo():
    logo = f"""

                                         ██████╗ ██╗   ██╗██╗██╗     ██████╗ ██╗   ██╗
                                        ██╔════╝ ██║   ██║██║██║     ██╔══██╗╚██╗ ██╔╝
                                        ██║  ███╗██║   ██║██║██║     ██║  ██║ ╚████╔╝ 
                                        ██║   ██║██║   ██║██║██║     ██║  ██║  ╚██╔╝  
                                        ╚██████╔╝╚██████╔╝██║███████╗██████╔╝   ██║   
                                         ╚═════╝  ╚═════╝ ╚═╝╚══════╝╚═════╝    ╚═╝                                                                                                                                           
                                                            Dev: NinjaRide
                                                            Server: .gg/silentzone   
\n"""
    print(Colorate.Horizontal(Colors.blue_to_green, Center.XCenter(logo)))



def check_token(token):

    bad_guilds = []
    all_guilds = []

    session = tls_client.Session(client_identifier="chrome_103")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36", 'authorization': f"{token}"}


    guilds = session.get(
        'https://discord.com/api/v9/users/@me/guilds?with_counts=true',
        headers=headers,
    ).json()

    if '401: unauthorized' in str(guilds).lower():
       return None, None, None

    elif 'you need to verify your account in order to perform this action.' in str(guilds).lower():
       return None, "verify", None

    total_guilds = len(guilds)
    data['guilds'] += total_guilds

    if total_guilds < config['minimum_servers']:

        all_guilds.extend(guild['id'] for guild in guilds)
        data['checked'] += 1
        return bad_guilds,total_guilds,all_guilds

    for guild in guilds:

        all_guilds.append(guild['id'])

        bad_guild = False

        if int(guild['approximate_member_count']) < config['minimum_members']:
           bad_guild = True

        elif int(guild['approximate_member_count']) > config['maximum_members']:
           bad_guild = True

        elif int(guild['approximate_presence_count']) < config['minimum_online']:
           bad_guild = True

        if config['full_check'] and not bad_guild and config['minimum_boosts'] != 0:

            boost_amount = session.get(f'https://discord.com/api/v9/guilds/{guild["id"]}', headers=headers).json()['premium_subscription_count']

            if boost_amount < config['minimum_boosts']:
               bad_guild = True


        if bad_guild:
            bad_guilds.append(guild["id"])
            data['invalid'] += 1

        else:
            data['valid'] += 1



    data['checked'] += 1

    return bad_guilds,total_guilds,all_guilds

def worker():
    while True:
        with locker:
            if len(tokens) != 0:
                token = tokens.pop(0)
            else:
                return

        bad_guilds,total_guilds,all_guilds = check_token(token)      

        if bad_guilds is not None:

            open("./output/guild_ids.txt","a", encoding='utf-8').write("\n".join(all_guilds)+'\n')

            if total_guilds < config['minimum_servers']:
                tprint(f"{Fore.LIGHTWHITE_EX}[{Fore.RED}-{Fore.LIGHTWHITE_EX}] LQ  {f'[{Fore.LIGHTRED_EX}{token}{Fore.LIGHTWHITE_EX}]':85} -> Below Min Servers: [{Fore.LIGHTRED_EX}{total_guilds}/{config['minimum_servers']}{Fore.LIGHTWHITE_EX}]")   
                open("output/underminservers.txt","a", encoding='utf-8').write(f"{token} | Below Min Servers\n")
                data['lq'] += 1

            elif len(bad_guilds) < config['good_token_max_bad_amount']:
                tprint(f"{Fore.LIGHTWHITE_EX}[{Fore.GREEN}+{Fore.LIGHTWHITE_EX}] UHQ {f'[{Fore.LIGHTGREEN_EX}{token}{Fore.LIGHTWHITE_EX}]':85} -> Good Guilds: [{Fore.LIGHTGREEN_EX}{total_guilds - len(bad_guilds)}/{total_guilds}{Fore.LIGHTWHITE_EX}]")   
                open("output/uhq.txt","a", encoding='utf-8').write(f"{token}\n")
                data['uhq'] += 1

            elif len(bad_guilds) < config['medium_token_max_bad_amount']:
                tprint(f"{Fore.LIGHTWHITE_EX}[{Fore.LIGHTYELLOW_EX}!{Fore.LIGHTWHITE_EX}] MQ  {f'[{Fore.LIGHTYELLOW_EX}{token}{Fore.LIGHTWHITE_EX}]':85} -> Good Guilds: [{Fore.LIGHTYELLOW_EX}{total_guilds - len(bad_guilds)}/{total_guilds}{Fore.LIGHTWHITE_EX}]")               
                open("output/mq.txt","a", encoding='utf-8').write(f"{token}\n")
                data['mq'] += 1

            else:
                tprint(f"{Fore.LIGHTWHITE_EX}[{Fore.RED}-{Fore.LIGHTWHITE_EX}] LQ  {f'[{Fore.LIGHTRED_EX}{token}{Fore.LIGHTWHITE_EX}]':85} -> Good Guilds: [{Fore.LIGHTRED_EX}{total_guilds - len(bad_guilds)}/{total_guilds}{Fore.LIGHTWHITE_EX}]")         
                open("output/lq.txt","a", encoding='utf-8').write(f"{token}\n")
                data['lq'] += 1
        elif total_guilds == "verify":
            tprint(f"{Fore.LIGHTWHITE_EX}[{Fore.RED}!{Fore.LIGHTWHITE_EX}] Unverified [{Fore.RED}{token}{Fore.LIGHTWHITE_EX}]")               
            open("output/verify.txt","a", encoding='utf-8').write(f"{token}\n")

        else:
            tprint(f"{Fore.LIGHTWHITE_EX}[{Fore.RED}!{Fore.LIGHTWHITE_EX}] Invalid [{Fore.RED}{token}{Fore.LIGHTWHITE_EX}]")               
            open("output/unauthorized.txt","a", encoding='utf-8').write(f"{token}\n")

                    
if __name__ == "__main__":

    logo()
    colorama.init(autoreset=True)
    config = yaml.safe_load(open("config.yaml", "r"))

    locker = threading.Lock()
    tokens = []
    threads = []
    thread_count = config['threads']


    for file in ["unauthorized.txt","underminservers.txt","verify.txt","lq.txt","uhq.txt","mq.txt","guild_ids.txt"]:
        open(f"./output/{file}", "w", encoding="utf8").close() 


    with open("./input/tokens.txt", encoding="utf-8") as file:  
        for token in file:
            raw_token = token

            if ":" in raw_token:
                raw_token = raw_token.split(":")
                tokens.extend(
                    item.strip()
                    for item in raw_token
                    if re.match(
                        r"(mfa\.[\w-]{84}|[\w-]{24}\.[\w-]{6}\.[\w-]{38}|[\w-]{24}\.[\w-]{6}\.[\w-]{27}|[\w-]{26}\.[\w-]{6}\.[\w-]{38})",
                        item,
                    )
                )
            else:
                tokens.append(raw_token.replace('\n',''))
            try:
                token
            except:
                continue  

    threading.Thread(target = cpm_counter, daemon=True).start()
    threading.Thread(target = update_title, daemon=True).start()

    for _ in range(thread_count):
        t = threading.Thread(target=worker, args= ())
        threads.append(t)
        t.start()

    [i.join() for i in threads]
            

    input(f"{Fore.LIGHTWHITE_EX}[{Fore.GREEN}+{Fore.LIGHTWHITE_EX}] Finished.")





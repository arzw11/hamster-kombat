import json
import requests
import time
from urllib.parse import unquote
from random import randint

from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView


from config.config import settings
from config.headers import headers
from config.proxy import proxy

class ClickHamster:
    def __init__(self, client:Client):
        self.client = client

    def get_web_data(self):
        with self.client:
            web_view =self.client.invoke(RequestWebView(
                    peer=self.client.resolve_peer('hamster_kombat_bot'),
                    bot=self.client.resolve_peer('hamster_kombat_bot'),
                    platform='android',
                    from_bot_menu=False,
                    url='https://hamsterkombat.io/'
                ))
            web_data = unquote(
                    string=unquote(
                        string=web_view.url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0]))
            return web_data
    
    def login_hamster(self, link: requests.Session, web_data):
        try:
            response= link.post(url='https://api.hamsterkombat.io/auth/auth-by-telegram-webapp', 
                                proxies=proxy, 
                                json={"initDataRaw": web_data})
            response.raise_for_status()
            auth_token = response.json()['authToken']
            return auth_token
        except Exception as erorr:
            return erorr

    def get_profile_data(self, link: requests.Session):
        try:
            response = link.post('https://api.hamsterkombat.io/clicker/sync', proxies=proxy, headers=headers, json={})
            response.raise_for_status()

            profile_data = response.json()['clickerUser']
            return profile_data
        except Exception as erorr:
            return erorr
    def get_boosts(self, link: requests.Session):
        try:
            response = link.post('https://api.hamsterkombat.io/clicker/boosts-for-buy', proxies=proxy, headers=headers, json={})
            response.raise_for_status()

            boosts = response.json()['boostsForBuy']
            return boosts
        except Exception as erorr:
            return erorr 
    def activation_boost(self, link: requests.Session, boost):
        try:
            response = link.post(url='https://api.hamsterkombat.io/clicker/buy-boost', 
                                 proxies=proxy,
                                 headers=headers,
                                json={'timestamp': 1, 'boostId': boost})
            response.raise_for_status()
            
            
            return True
        except Exception as erorr:
            return False
    def click_hamster(self, link: requests.Session, available_energy: int, click: int):
        try:
            response = link.post('https://api.hamsterkombat.io/clicker/tap',
                                 proxies=proxy,
                                 headers=headers,
                                 json={'availableTaps': available_energy, 'count': click, 'timestamp': time()})
            response.raise_for_status()

            player_data = response.json()['clickerUser']
            return player_data
        except Exception as erorr:
            return erorr
    def run(self):
        with requests.Session() as link:
            while True:
                flag = False
                web_data = self.get_web_data()
                auth_token = self.login_hamster(link=link, web_data=web_data)
            
                headers["Authorization"] = f"Bearer {auth_token}"

                profile_data = self.get_profile_data(link=link)

                available_energy = profile_data['availableTaps']
                balance = profile_data['balanceCoins']

                

                click = randint(a=settings.CLICKS[0], b=settings.CLICKS[1])
                
                player_data = self.click_hamster(link=link, available_energy= available_energy, click=click)

                available_energy = player_data['availableTaps']
                new_balance = int(player_data['balanceCoins'])
                calc_click = new_balance - balance
                balance = new_balance

                boosts = self.get_boosts(link=link)[-1]
                
                print(f'Доступная энергия: {available_energy}\nБаланс: {balance}\nКлики: {calc_click}')
                print()
                
                if int(available_energy) < settings.MIN_ENERGY and boosts['cooldownSeconds'] == 0 and boosts['level'] <= boosts['maxLevel']:
                    status = self.activation_boost(link=link, boost= "BoostFullAvailableTaps")
                    if status:
                        print('Активация буста')
                        flag = True
                        time.sleep(5)
                        
                if int(available_energy) < settings.MIN_ENERGY and flag == False:        
                    print(f"Энергия закончилась. Осталось {settings.SLEEP_TIME} секунд")
                    time.sleep(settings.SLEEP_TIME)


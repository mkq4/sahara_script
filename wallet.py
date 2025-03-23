import asyncio
import pandas as pd

from random import shuffle
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from playwright.async_api import BrowserContext
from web3 import Web3
from eth_account import Account
from loguru import logger

from config import MINT_NFT
from dapps.NFT import NFT
from dapps.Galxe import Galxe
from dapps.Sahara import Sahara
from utils import USER_AGENTS, parse_proxy
from random import choice


wallets_data: [str, str, str] = []

sahara_rpc: str = "https://testnet.saharalabs.ai"
w3 = Web3(Web3.HTTPProvider(sahara_rpc))

seeds_file = 'data/seeds.txt'
proxy_file = 'data/proxy.txt'

class Wallet:
    def __init__(self, 
                 account: str,
                 seed: str,
                 proxy: dict,
                 address: str,
                 second_address: str,
                 user_agent: str,
                 balance: int
                 ):
        
        self.account = account
        self.seed = seed
        self.proxy = proxy
        self.address = address
        self.second_address = second_address
        self.user_agent = user_agent
        self.balance = balance
        self.sheet_data = ["", "", "", ""]


    def __str__(self):
        return (
            f"address = {self.address}\n"
            f"second_address = {self.second_address}\n"
            f"proxy = {self.proxy}\n"
            f"tx = {w3.eth.get_transaction_count(w3.to_checksum_address(self.address))}"
        )



if not w3.is_connected():
    logger.error(f"Error connecting to blockchain")
    exit()

Account.enable_unaudited_hdwallet_features()

WALLETS = []

def get_second_address(mnemonic: str):
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

    wallet = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)

    second_address = wallet.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(
        1).PublicKey().ToAddress()

    return second_address

def create_wallets():
    with open(seeds_file, 'r') as file:
        seeds: list[str] = [seed.strip() for seed in file.readlines()]

    with open(proxy_file, 'r') as file:
        proxies = [proxy.strip() for proxy in file.readlines()]
    new_proxies = []

    for proxy in proxies:
        new_proxy = parse_proxy(proxy)
        new_proxies.append(new_proxy)

    #print(new_proxies)

    proxy_seed_pairs = list(zip(new_proxies, seeds))

    for proxy, seed in proxy_seed_pairs:
        account = Account.from_mnemonic(seed)
        address = account.address

        balance = w3.from_wei(w3.eth.get_balance(address), 'ether')

        user_agent = choice(USER_AGENTS)

        second_address = get_second_address(seed)

        wallet = Wallet(
            account=account,
            seed=seed,
            proxy=proxy,
            address=address,
            second_address=second_address,
            balance=balance,
            user_agent=user_agent
        )
        WALLETS.append(wallet)

create_wallets()

shuffle(WALLETS)

async def wallet_process(wallet: Wallet, context: BrowserContext):
    #init galxe and sahara
    galxe = Galxe(wallet, context)
    sahara = Sahara(wallet, context)

    logger.info("Starting Galxe")
    await galxe.connect_wallet()
    await galxe.complete_tasks()
    logger.info("Completed Galxe")

    await asyncio.sleep(5)
    logger.info("Starting Sahara")

    await sahara.connect_wallet()
    await sahara.tx_task()
    await sahara.claim_tasks()

    if MINT_NFT:
        nft = NFT(wallet=wallet)
        await nft.start()

    wallet.sheet_data[0] = wallet.address
    wallet.sheet_data[1] = str(w3.from_wei(w3.eth.get_balance(w3.to_checksum_address(wallet.address)), "ether"))[:6]
    wallet.sheet_data[3] = str(w3.eth.get_transaction_count(w3.to_checksum_address(wallet.address)))
    wallets_data.append(wallet.sheet_data)
    # print(wallets_data)




def print_data():

    sheet = pd.DataFrame(wallets_data, columns=['address', '$SAH', 'puzzles', 'tx count'])

    # Сбрасываем индексы и начинаем их с 1
    sheet = sheet.reset_index(drop=True)
    sheet.index = sheet.index + 1

    # Настройки вывода
    pd.set_option('display.colheader_justify', 'center')  # Выравнивание заголовков
    pd.set_option("display.max_columns", None)  # Показывать ВСЕ столбцы
    pd.set_option("display.max_colwidth", None)  # Не обрезать текст в ячейках

    print(sheet)

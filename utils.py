import asyncio
import re
from typing import Dict

from web3 import Web3
from playwright.async_api import BrowserContext, Page
from loguru import logger

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.180 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12.6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:117.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/117.0.2045.55",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.93 Safari/537.36",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:116.0) Gecko/20100101 Firefox/116.0",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6015.42 Safari/537.36",
]

def parse_proxy(proxy_str: str) -> dict:
    # Формат: ip:port@login:pass, например "192.168.1.1:8080@user1:pass1"
    # Используем регулярное выражение для извлечения данных
    pattern = r'([^@]+)@([^:]+):(.+)'
    match = re.match(pattern, proxy_str.strip())

    if match:
        server, username, password = match.groups()
        # Добавляем протокол http:// к server, если его нет
        if not server.startswith('http'):
            server = f'http://{server}'
        return {
            'server': server,
            'username': username,
            'password': password
        }
    else:
        # Если строка не соответствует формату, возвращаем пустой объект
        print(f"Неверный формат прокси: {proxy_str}")
        return {
            'server': '',
            'username': '',
            'password': ''
        }

async def confirm_mm(context: BrowserContext):
    try:
        await asyncio.sleep(3)
        pages = context.pages

        # mm_page: Page = [page for page in pages if page.url.startswith('chrome-extension:/')][0]
        mm_page: Page = pages[-1]

        if not mm_page.url.startswith('chrome-extension://'):
            return Exception("Cound't finded mm page")

        await mm_page.bring_to_front()

        possible_selectors = ['confirm-btn', 'confirm-footer-button', 'confirmation-submit-button']

        while mm_page:
            #confirming
            for selector in possible_selectors:

                #mm page exist?
                if context.pages[-1].url.startswith('chrome-extension://'):
                    confirm_btn = mm_page.get_by_test_id(selector)

                    if not await confirm_btn.is_visible(timeout=5000):
                        continue
                    else:
                        logger.info("Selector found")
                        await confirm_btn.click()
                        await asyncio.sleep(3)

                else: return
            await asyncio.sleep(4)
        #confirm_btn = mm_page
    except Exception as e:
        logger.error(e)

async def get_gas_params() -> Dict[str, float]:
    sahara_rpc: str = "https://testnet.saharalabs.ai"
    w3 = Web3(Web3.HTTPProvider(sahara_rpc))

    last_block = await w3.eth.get_block('latest')
    base_fee = last_block['baseFeePerGas']
    max_priority_fee = await w3.eth.max_priority_fee
    max_fee = base_fee + max_priority_fee

    return {
        "maxFeePerGas": max_fee,
        "maxPriorityFeePerGas": max_priority_fee,
    }

NFT_ABI = [
    {
        "constant": True,
        "inputs": [
            {
                "name": "owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "balance",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

sahara_chain = {
    "network_name": "SaharaAI Testnet",
    "rpc": "https://testnet.saharalabs.ai",
    "chain_id": "313313",
    "currency_symbol": "SAHARA",
    "explorer": "https://testnet-explorer.saharalabs.ai",
}

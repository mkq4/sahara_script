import asyncio
import random

import config
from config import DELAY_BETWEEN_ACCS

from metamask.restore_wallet import restore_wallet
from playwright.async_api import async_playwright

from wallet import WALLETS, wallet_process, print_data

from loguru import logger


async def main():
    for wallet in WALLETS:
        async with async_playwright() as p:
            proxy = None
            context_kwargs = {
                'headless': False,
                'args': [
                    f"--disable-extensions-except={config.MM_PATH}",
                    f"--load-extension={config.MM_PATH}",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                ],
                'slow_mo': 200,
                'user_agent': wallet.user_agent,
            }

            if proxy:
                context_kwargs['proxy'] = {
                    'server': proxy['server'],
                    'username': proxy['username'],
                    'password': proxy['password'],
                }

            context = await p.chromium.launch_persistent_context('', **context_kwargs)

            await asyncio.sleep(2)
            
            try:
                logger.info(f"Starting wallet - {wallet.address}")

                # await restore_wallet(context=context, wallet=wallet)
                await wallet_process(wallet=wallet, context=context)

            except Exception as e:
                logger.error(f'Error | {e}')

        if wallet.address != WALLETS[-1].address:
            delay = random.randint(DELAY_BETWEEN_ACCS[0], DELAY_BETWEEN_ACCS[1])
            logger.info(f"sleeping {delay} sec between wallets")
            await asyncio.sleep(delay)

    print_data()
    logger.success('All wallets end 🦍')
    logger.success('🐒 tg - @cryptomakaquich 🐒')


if __name__ == '__main__':
    asyncio.run(main())
import asyncio

from playwright.async_api import BrowserContext, Page
from loguru import logger
from web3 import Web3
from random import uniform
from config import SAHARA_AMOUNT

from utils import confirm_mm, get_gas_params

sahara_url: str = "https://legends.saharalabs.ai/"
sahara_rpc: str = "https://testnet.saharalabs.ai"



class Sahara:
    def __init__(self, wallet, context: BrowserContext):
        self.wallet = wallet
        self.context = context

    async def connect_wallet(self):
        max_attempts = 3
        attempt = 1

        while attempt <= max_attempts:
            sahara_page: Page = None
            mm_page: Page = None
            try:
                # Открываем новую страницу
                sahara_page = await self.context.new_page()
                await sahara_page.bring_to_front()
                logger.info(f"Attempt {attempt}/{max_attempts}: Opening Sahara page")
                await sahara_page.goto(sahara_url, timeout=120000)
                await sahara_page.wait_for_load_state()

                logger.info('Starting connecting wallet')
                sign_in = sahara_page.get_by_text("Sign In", exact=True).first
                await sign_in.click()

                await (sahara_page.get_by_text("MetaMask", exact=True)).click()

                # Ждем открытия MetaMask
                await asyncio.sleep(3)
                # mm_page = self.context.pages[-1]  # Последняя открытая страница — MetaMask

                # Первая кнопка подтверждения
                await confirm_mm(context=self.context)

                logger.success('Wallet connected successfully')
                return  # Успешно подключились, выходим

            except TimeoutError as e:
                logger.error(f"Attempt {attempt}/{max_attempts}: Timeout error - {e}")
                if mm_page and await mm_page.get_by_test_id("confirmation-cancel-button").count() > 0:
                    await mm_page.get_by_test_id("confirmation-cancel-button").click(timeout=5000)
                attempt += 1
                await asyncio.sleep(2)  # Пауза перед новой попыткой

            except Exception as e:
                logger.error(f"Attempt {attempt}/{max_attempts}: Error - {e}")
                if mm_page and await mm_page.get_by_test_id("confirmation-cancel-button").count() > 0:
                    await mm_page.get_by_test_id("confirmation-cancel-button").click(timeout=5000)
                attempt += 1
                await asyncio.sleep(2)  # Пауза перед новой попыткой


    async def claim_tasks(self):
        try:
            # Находим страницу Sahara
            sahara_page: Page = next((page for page in self.context.pages if page.url == sahara_url), None)
            if not sahara_page:
                raise Exception("Sahara page not found")

            await sahara_page.reload()
            await sahara_page.wait_for_load_state()

            #get amount puzzles
            puzzles = await sahara_page.locator('[class="amount"]').inner_text()
            self.wallet.sheet_data[2] = puzzles

            # Кликаем на кнопку задач
            # await asyncio.Future()
            try:
                await sahara_page.locator('[src="/assets/all-normal-BQuqrsj0.png"]').click()
            except Exception as e:
                logger.error("Not found locator", e)
                await sahara_page.locator('[src="/assets/all-claim-D56aap8V.png"]').click()

            await asyncio.sleep(3)

            # Получаем локатор для задач
            for _ in range(5):
                try:
                    tasks = sahara_page.locator('[xmlns="http://www.w3.org/2000/svg"]')
                    # tasks = tasks.locator("..") #родительские элементы

                    if tasks:
                        logger.info(f"Task found")

                    # Получаем все элементы задач и берем последние 3
                    task_elements = await tasks.all()

                    for task in task_elements:
                        await task.click(force=True)
                        await asyncio.sleep(1)
                except Exception as e:
                    logger.error('Claiming task error', e)

            #claim task
            for _ in range(5):
                try:
                    tasks_elements = await sahara_page.locator('[class="task-button-plus"]').all()

                    for task in tasks_elements:
                        await task.click()
                        await asyncio.sleep(1)
                except Exception as e:
                    logger.error('Claiming task error', e)

        except Exception as e:
            logger.error(f"Error at claim_tasks: {e}")
            raise

    async def tx_task(self):
        logger.info("Starting send tx")
        w3 = Web3(Web3.HTTPProvider(sahara_rpc))

        if not w3.is_connected():
            raise "Couldn't connect to Sahara"

        tx = {
            "to": self.wallet.second_address,
            "value": w3.to_wei(uniform(SAHARA_AMOUNT[0], SAHARA_AMOUNT[1]), 'ether'),
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(w3.to_checksum_address(self.wallet.address)),
            "gas": 200000,
            "chainId": w3.eth.chain_id,
        }

        signed_tx = w3.eth.account.sign_transaction(tx, self.wallet.account.key)

        try:
            send_tx = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            logger.info(f"Transaction sent! Hash: 0x{send_tx.hex()}")

            receipt = w3.eth.wait_for_transaction_receipt(send_tx)

            if receipt['status'] == 1:
                logger.success("Transaction was successful!")
            else:
                logger.error("Transaction failed!")

            return receipt

        except Exception as e:
            logger.error(f"An error occurred while sending the transaction: {str(e)}")
            return None
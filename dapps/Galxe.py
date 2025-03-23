import asyncio

from playwright.async_api import BrowserContext, Page
from loguru import logger
from utils import confirm_mm

galxe_url:str = "https://app.galxe.com/quest/SaharaAI/GCNLYtpFM5"

class Galxe:

    def __init__(self, wallet, context: BrowserContext):
        self.wallet = wallet
        self.context = context

    async def connect_wallet(self):
        for _ in range(3):
            try:
                galxe_page: Page = await self.context.new_page()
                await galxe_page.bring_to_front()
                await galxe_page.goto(galxe_url, timeout=120000)
                await galxe_page.wait_for_load_state()

                #connect wallet btn
                await galxe_page.get_by_text('Log in', exact=True).first.click()

                await galxe_page.get_by_text('MetaMask', exact=True).first.click()
                #mm confirm
                await confirm_mm(context=self.context)
                break
            except:
                continue

    async def complete_tasks(self):

        try:
            galxe_page: Page = await self.context.new_page()
            await galxe_page.bring_to_front()
            await galxe_page.goto(galxe_url, timeout=120000)
            await galxe_page.wait_for_load_state()


            task_text = ["Daily Visit the Sahara AI Twitter", "Daily Visit the Sahara AI Blog"]

            for text in task_text:
                await asyncio.sleep(1)
                task = galxe_page.get_by_text(text, exact=True)
                await task.scroll_into_view_if_needed()
                await asyncio.sleep(2)
                await task.click()
                logger.info("clicked")

                try:
                    confirm_popup = galxe_page.get_by_text("Continue to Access", exact=True)
                    if await confirm_popup.is_visible():
                        await confirm_popup.click()
                except Exception:
                    logger.info("Confirm popup not found")

                await asyncio.sleep(2)

                await galxe_page.bring_to_front()


        except Exception as e:
            logger.error("Error completing Galxe, retrying")

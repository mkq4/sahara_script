import config
import asyncio

from playwright.async_api import BrowserContext, Page
from loguru import logger
from wallet import Wallet
from utils import sahara_chain


async def restore_wallet(context: BrowserContext, wallet: Wallet) -> bool:

    try:
        logger.info(f'{wallet.address} | Starting recover wallet')
        page = context.pages[0]

        await page.goto(f'chrome-extension://{config.MM_EXTENTION_IDENTIFIER}/home.html#onboarding/welcome')
        await page.bring_to_front()
        await page.wait_for_load_state()

        # Agree checkbox
        await page.get_by_test_id('onboarding-terms-checkbox').click()

        # import wallet btn
        await page.get_by_test_id('onboarding-import-wallet').click()

        # no, thanks
        await page.get_by_test_id('metametrics-no-thanks').click()

        # fill seed phrase
        for i, word in zip(range(12), wallet.seed.split()):
            await page.locator(f'//*[@id="import-srp__srp-word-{i}"]').fill(word)

        # confirm secret phrase
        await page.get_by_test_id('import-srp-confirm').click()

        # fill password
        await page.get_by_test_id('create-password-new').fill(config.MM_EXTENTION_PASSWORD)
        await page.get_by_test_id('create-password-confirm').fill(config.MM_EXTENTION_PASSWORD)

        # agree checkbox
        await page.get_by_test_id('create-password-terms').click()

        # import wallet btn
        await page.get_by_test_id('create-password-import').click()

        # done
        await page.get_by_test_id('onboarding-complete-done').click()

        # next
        await page.get_by_test_id('pin-extension-next').click()

        # done
        await page.get_by_test_id('pin-extension-done').click()

        await create_and_change_network(chain_data=sahara_chain, page=page)

        logger.success(f'{wallet.address} | Wallet Ready To Work')
        # await page.close()


        return True

    except Exception as err:
        logger.error(f'{wallet.address} | Not Recovered ({err})')
        logger.info(f'Error when getting an account, trying again')

    return False

async def create_and_change_network(chain_data: dict, page: Page):

    # changing network
    logger.info("Changing network")
    await page.get_by_test_id("network-display").click()

    # add btn
    await page.get_by_text('Add a custom network', exact=True).click()

    # fill inputs
    await page.get_by_test_id("network-form-network-name").fill(chain_data["network_name"])

    logger.info("adding rpc")
    await page.get_by_test_id("test-add-rpc-drop-down").click()
    await page.get_by_text("Add RPC URL", exact=True).click()

    # fill rpc url
    await page.get_by_test_id("rpc-url-input-test").fill(chain_data["rpc"])
    await page.get_by_text("Add URL", exact=True).click()

    # add chain id
    await page.get_by_test_id("network-form-chain-id").fill(chain_data["chain_id"])

    # currency symbol
    await page.get_by_test_id("network-form-ticker-input").fill(chain_data["currency_symbol"])

    # explorer
    await page.get_by_test_id("test-explorer-drop-down").click()
    await page.get_by_text("Add a block explorer URL", exact=True).click()
    await page.get_by_test_id("explorer-url-input").fill(sahara_chain["explorer"])
    await page.get_by_text("Add URL", exact=True).click()

    # save
    await page.get_by_text("Save", exact=True).click()

    logger.info("Network added")

    await page.get_by_test_id("network-display").click()
    await page.get_by_test_id(chain_data["network_name"]).click()

    logger.success(f"Network {chain_data["network_name"]} Changed")
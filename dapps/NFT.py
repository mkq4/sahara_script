import asyncio

from loguru import logger
from web3 import Web3
from utils import NFT_ABI
from random import shuffle


sahara_rpc: str = "https://testnet.saharalabs.ai"
cosmic_nft_address: str = "0x547108FCe3fE3D7BdE52C8b2f9CBBED53eAB3874"
genesis_nft_address: str = "0x5a4fD0F6499d26b9A8A4A66536a536a1C4787DDd"
sahara_nft_address: str = "0xC3622849B5E11A7c1D71276D6dc66Fb59eaAa038"

class NFT:
    def __init__(self, wallet):
        self.wallet = wallet
        self.w3 = Web3(Web3.HTTPProvider(sahara_rpc))
        self.nft_amount = self.check_nft()

    def mint_nft(self, contract_address: str):
        address = self.wallet.address[2:].zfill(64)
        method = "0x84bb1e42"
        data = ""
        value = self.w3.to_wei(0, "ether")

        if contract_address == cosmic_nft_address:
            data = method + address + "0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000001800000000000000000000000000000000000000000000000000000000000000080ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

        if contract_address == genesis_nft_address:
            data = method + address + "0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000000000000000000000000000000000000000016000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

        if contract_address == sahara_nft_address:
            balance = self.w3.eth.get_balance(self.w3.to_checksum_address(address))
            balance = self.w3.from_wei(balance, "ether")
            if balance > 0.1:
                data = method + address + "0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000016345785d8a000000000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000000000000000000000000000000000000000016000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
                value = self.w3.to_wei(0.1, "ether")
            else:
                logger.warning(f"Balance not enough for sahara nft | {balance} (expected > 0.1)")
                return

        tx = {
            "from": self.w3.to_checksum_address(self.wallet.address),
            "to": self.w3.to_checksum_address(contract_address),
            "value": value,
            "gas": 200000,
            "data": data,
            "gasPrice": self.w3.eth.gas_price,
            "nonce": self.w3.eth.get_transaction_count(self.w3.to_checksum_address(self.wallet.address)),
            "chainId": self.w3.eth.chain_id,
        }

        sign_tx = self.w3.eth.account.sign_transaction(tx, self.wallet.account.key)

        try:
            send_tx = self.w3.eth.send_raw_transaction(sign_tx.raw_transaction)
            logger.info(f"Transaction sent 0x{send_tx.hex()}")

            receipt = self.w3.eth.wait_for_transaction_receipt(send_tx)

            if receipt['status'] == 1:
                logger.success("Transaction was successful!")
            else:
                logger.error("Transaction failed!")

        except Exception as e:
            logger.error(e)

    def check_nft(self):
        contracts = [cosmic_nft_address, genesis_nft_address, sahara_nft_address]
        shuffle(contracts)
        result = {}

        for c in contracts:
            contract = self.w3.eth.contract(address=self.w3.to_checksum_address(c), abi=NFT_ABI)
            balance = contract.functions.balanceOf(self.wallet.address).call()

            result[c] = balance

        return result

    async def start(self):
        logger.info("Looking for available NFT")

        for k, v in self.nft_amount.items():
            if v < 1:
                logger.info(f"NFT to mint - founded")
                self.mint_nft(k)
                break

        logger.info("No available NFT to mint")

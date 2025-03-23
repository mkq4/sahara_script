USE_PROXY: bool = True
MM_EXTENTION_IDENTIFIER: str = 'nkbihfbeogaeaoehlefnkodbefgpgknn'
MM_EXTENTION_PASSWORD = "qwerty123"

'''
Dont forger to fill proxy in data/proxy.txt file
and seeds in data/seeds.txt file 
then start main.py
'''

'''
download metamask extention from your browser
https://stackoverflow.com/questions/14543896/where-does-chrome-store-extensions

unpack folder data in metamask/metamask

change path to mm on your pc
'''

MM_PATH = '/Users/user/Desktop/dev/python/SaharaAi_daily_script/metamask/metamask'


SAHARA_AMOUNT: (float, float) = (0.001, 0.0001) #random tx value
DELAY_BETWEEN_ACCS: (int, int) = (15, 60) #in seconds

#minting only one random nft (of 3)
MINT_NFT: bool = False
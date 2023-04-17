from web3 import Web3
import time
import requests
import random

delay = [20, 50]
slippage = 1

class Network:
    rpc_chain = "https://arb1.arbitrum.io/rpc"
    chain_id = "42161"
    
class Data:
    token_address = "0x09E18590E8f76b6Cf471b3cd75fE1A1a9D2B2c2b"
    nativeEth_address = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    token_abi = [{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]

web3 = Web3(Web3.HTTPProvider(Network.rpc_chain))

def api_call(url):
    try:
        call_data = requests.get(url)
    except Exception as e:
        print(e)
        return api_call(url)
    try:
        api_data = call_data.json()
        return api_data
    except Exception as e:
        print(call_data.text)

def balanceOf(wallet_address):
    token = web3.eth.contract(address=web3.toChecksumAddress(Data.token_address), abi=Data.token_abi)
    balance = token.functions.balanceOf(wallet_address).call()
    return balance

def check_allowance(wallet_address):
    allowance_url = f'https://api.1inch.io/v5.0/{Network.chain_id}/approve/allowance?tokenAddress={Data.token_address}&walletAddress={wallet_address}'
    allowance_data = api_call(allowance_url)
    allowance = int(allowance_data["allowance"])
    return allowance

def inch_approve(private_key):
    account = web3.eth.account.privateKeyToAccount(private_key)
    wallet_address = account.address
    amount = balanceOf(wallet_address)
    try:
        _1inchurl = f'https://api.1inch.io/v5.0/{Network.chain_id}/approve/transaction?tokenAddress={Data.token_address}&amount={amount}'
        json_data = api_call(_1inchurl)
        tx = {
            "nonce": web3.eth.getTransactionCount(wallet_address),
            "to": web3.toChecksumAddress(json_data["to"]),
            "data": json_data["data"],
            "gasPrice": int(web3.eth.gas_price * 1.1),
            "gas": 2000000
        }
        signed_tx = web3.eth.account.signTransaction(tx, private_key)
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

        print(f'\n>>> Succes approve $AIDOGE : https://arbiscan.io/tx/{web3.toHex(tx_hash)}')
        print(f'    {wallet_address}')
    except Exception as error:
        print(f'\n>>> Error approve $AIDOGE | {error}')
        print(f'    {wallet_address}')

def inch_swap(private_key):
    account = web3.eth.account.privateKeyToAccount(private_key)
    wallet_address = account.address
    nonce = web3.eth.getTransactionCount(wallet_address)
    try:
        amount = balanceOf(wallet_address)
        if amount == 0:  # добавьте проверку на ноль
            print(f'\n>>> Zero balance of $AIDOGE token.')
            print(f'    {wallet_address}')
            return
        allowance = check_allowance(wallet_address)
        if allowance >= amount:
            print(f'\n>>> token $AIDOGE Already approved')
            print(f'    {wallet_address}')
        else:
            inch_approve(private_key)
            time.sleep(random.randint(delay[0], delay[1]))
        _1inchurl = f'https://api.1inch.io/v5.0/{Network.chain_id}/swap?fromTokenAddress={Data.token_address}&toTokenAddress={Data.nativeEth_address}&amount={amount}&fromAddress={wallet_address}&slippage={slippage}&destReceiver={wallet_address}'
        json_data = api_call(_1inchurl)
        received_eth = web3.fromWei(int(json_data["toTokenAmount"]), 'ether')
        tx = json_data['tx']
        tx['nonce'] = nonce
        tx['to'] = Web3.toChecksumAddress(tx['to'])
        tx['gasPrice'] = int(tx['gasPrice'])
        tx['value'] = int(tx['value'])
        signed_tx = web3.eth.account.signTransaction(tx, private_key)
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

        print(f'\n>>> swap all $AIDOGE to {round(received_eth, 5)} $ETH | https://arbiscan.io/tx/{web3.toHex(tx_hash)}')
        print(f'    {wallet_address}')
    except Exception as error:
        print(f'\n>>> Error swap | {error}')
        print(f'    {wallet_address}')

def main():
    with open("wallets.txt", "r") as f:
        private_keys = [row.strip() for row in f if row.strip()]
    print(f'developed by th0masi [https://t.me/thor_lab]')
    print(f'Number of wallets: {len(private_keys)}')

    for private_key in private_keys:
        private_key = private_key.strip()
        inch_swap(private_key)
        time.sleep(random.randint(delay[0], delay[1]))

if __name__ == "__main__":
    main()
import os
import time

import eth_account
import requests
from dotenv import load_dotenv, find_dotenv
from eth_account import Account
from hyperliquid.utils.signing import sign_l1_action
from hyperliquid.utils.constants import TESTNET_API_URL, MAINNET_API_URL
from hyperliquid.exchange import Exchange
env_path = find_dotenv()
load_dotenv(env_path)
PRIVATE_KEY = os.getenv("PRIVATE_KEY")


def signing(action, nonce):
    wallet = eth_account.Account.from_key(PRIVATE_KEY)
    return sign_l1_action(wallet, action, None, nonce, False)


def generatePayload(action):
    nonce = int(time.time()) * 1000
    signature = signing(action, nonce)
    payload = {
        "action": action,
        "nonce": nonce,
        "signature": signature,
        "vaultAddress": None
    }
    return payload

def send_payload(payload):
    print(payload)
    url = TESTNET_API_URL + "/exchange"
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    response = session.post(url, json=payload)
    print(response)
    try:
        print(response.json())
    except:
        print(response.text)

def step1(): # registering token
    TokenSpec = {
        "name": "TUSDE",
        "szDecimals": 2,
        "weiDecimals": 8
    }

    RegisterToken2 = {
        "spec": TokenSpec,
        "maxGas": 28000 * 10**8,
        "fullName": TokenSpec["name"]
    }

    action = {"type": "spotDeploy", "registerToken2": RegisterToken2}
    nonce = int(time.time()) * 1000

    # exchange = Exchange(TESTNET_API_URL)
    signature = signing(action, nonce)
    payload = {
        "action": action,
        "nonce": nonce,
        "signature": signature,
        "vaultAddress": None
    }
    send_payload(payload)
initial_supply = 100_000_000_000 #100b
initial_supply_wei = initial_supply * 10**8

def step2(): #set user genesis balance
    UserGenesis = {
        "token": 1295,
        "userAndWei": [("0x0d20d44Fbd48752241a2b18979dF2424e8a5F022".lower(), str(initial_supply_wei))],
        "existingTokenAndWei": []
    }
    action = {"type": "spotDeploy", "userGenesis": UserGenesis}
    nonce = int(time.time()) * 1000
    signature = signing(action, nonce)
    payload = {
        "action": action,
        "nonce": nonce,
        "signature": signature,
        "vaultAddress": None
    }
    send_payload(payload)


def step3(): #xulian says skip
    Genesis = {
        "token": 1295,
        "maxSupply": str(int(initial_supply_wei)),
        "noHyperliquidity": True
    }
    action = {"type": "spotDeploy", "genesis": Genesis}
    payload = generatePayload(action)
    send_payload(payload)

def step4():
    RegisterSpot = {
        "tokens": [1295, 0]
    }
    action = {"type": "spotDeploy", "registerSpot": RegisterSpot}
    payload = generatePayload(action)
    send_payload(payload)

def step5():
    RegisterHyperliquidity = {
        "spot": 1176,
        "startPx": "0.01",
        "orderSz": "0",
        "nOrders": 0,
        "nSeededLevels": 0
    }
    action = {"type": "spotDeploy", "registerHyperliquidity": RegisterHyperliquidity}
    payload = generatePayload(action)
    send_payload(payload)



if __name__ == "__main__":
    wallet = eth_account.Account.from_key(PRIVATE_KEY)
    print(wallet.address)
    print(initial_supply_wei)
    step5()

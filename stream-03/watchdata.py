from typing import Optional

import requests
from retry import retry


class Blockchain:
    ETH = 'eth'
    POLYGON = 'polygon'
    BSC = 'bsc'


FORKS_DEPTH = {
    Blockchain.ETH: 10,
    Blockchain.POLYGON: 10,
    Blockchain.BSC: 10,
}

URLS = {
    Blockchain.ETH: 'https://ethereum.api.watchdata.io',
    Blockchain.POLYGON: 'https://polygon.api.watchdata.io',
    Blockchain.BSC: 'https://bsc.api.watchdata.io',
}

HEADERS = {
    Blockchain.ETH: dict(api_key='a2e18f64-52cf-4ad5-a397-465587963522'),
    Blockchain.POLYGON: dict(api_key='6172be99-fdad-48cf-833c-1787d4928034'),
    Blockchain.BSC: dict(api_key='4b58565b-c9b0-4307-b29a-4b268317cd0d'),
}


@retry(tries=3, delay=0.5)
def get_last_block_number(blockchain: str) -> int:
    r = requests.get(f'{URLS[blockchain]}/watch_filters/lastBlockNumber', headers=HEADERS[blockchain])
    return r.json()['block_number'] - FORKS_DEPTH[blockchain]


@retry(tries=3, delay=0.5)
def add_filter(blockchain: str, address: str, contract_address: Optional[str] = None):
    json = dict(address=address.lower())
    if contract_address is not None:
        json |= dict(contract_address=contract_address)

    r = requests.post(f'{URLS[blockchain]}/watch_filters/add', json=json, headers=HEADERS[blockchain])

    return r.json()['filter_id']


@retry(tries=3, delay=0.5)
def check_filters(blockchain: str, block_number: int) -> list:
    json = dict(block_number=block_number)

    r = requests.post(f'{URLS[blockchain]}/watch_filters/check', json=json, headers=HEADERS[blockchain])

    return r.json()['filters']


@retry(tries=3, delay=0.5)
def remove_filter(blockchain: str, filter_id: str) -> list:
    json = dict(filter_id=filter_id)

    r = requests.delete(f'{URLS[blockchain]}/watch_filters/remove', json=json, headers=HEADERS[blockchain])

    return r.json()['detail']


@retry(tries=3, delay=0.5)
def filter_info(blockchain: str, address: str) -> list:
    json = dict(address=address)

    r = requests.post(f'{URLS[blockchain]}/watch_filters/info', json=json, headers=HEADERS[blockchain])

    return r.json()['filters']


@retry(tries=3, delay=0.5)
def filter_all(blockchain: str) -> list:
    r = requests.post(f'{URLS[blockchain]}/watch_filters/all', headers=HEADERS[blockchain])

    return r.json()


def get_balance(blockchain: str, address: str) -> int:
    json = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [f"{address}", "latest"],
        "id": 0
    }
    r = requests.post(f'{URLS[blockchain]}/node/jsonrpc', json=json, headers=HEADERS[blockchain])

    return int(r.json()['result'], 16) / 10**18

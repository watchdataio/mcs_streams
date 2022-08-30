from watchdata import Blockchain
from watchdata import add_filter
from watchdata import check_filters

if __name__ == '__main__':

    add_filter(blockchain=Blockchain.POLYGON, address='0x93dF93ca704D08B52B479d8a61504c8FD7919Af4'.lower(),
               contract_address='0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'.lower())
    result = check_filters(blockchain=Blockchain.POLYGON, block_number=32346392)
    print(result)

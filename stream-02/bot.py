from watchdata import Blockchain
from watchdata import add_filter
from watchdata import filter_info
from watchdata import remove_filter

if __name__ == '__main__':

    add_filter(blockchain=Blockchain.ETH, address='0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45'.lower())

    filter_id = filter_info(
        blockchain=Blockchain.POLYGON, address='0x93dF93ca704D08B52B479d8a61504c8FD7919Af4'.lower()
    )[0]['filter_id']

    # remove_filter(blockchain=Blockchain.POLYGON, filter_id=filter_id)

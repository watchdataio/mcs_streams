import json
from time import sleep

import requests

from models import get_objects_by_addresses
from watchdata import Blockchain
from watchdata import check_filters
from watchdata import get_last_block_number


def send_message(message: str, chat_id: str, bot_token: str = 'YOUR_TOKEN'):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    response = requests.post(
        url=url,
        json={
            'chat_id': chat_id,
            'text': message,
        },
        timeout=0.5,
    )
    print(response.text)
    if response.status_code == 200:
        print(f'SEND MESSAGE TO {chat_id}')


def get_local_last_blocks():
    with open('last_blocks', 'r') as file:
        last_blocks = file.read()

    if not last_blocks:
        last_blocks = dict(
            polygon=get_last_block_number(Blockchain.POLYGON),
            bsc=get_last_block_number(Blockchain.BSC),
            eth=get_last_block_number(Blockchain.ETH),
        )
        set_local_last_blocks(last_blocks)
        return last_blocks

    return json.loads(last_blocks)


def set_local_last_blocks(last_blocks):
    with open('last_blocks', 'w') as file:
        file.write(json.dumps(last_blocks))


def sync_transfers():
    """
    Основной метод нашего процессора для получения новых трансферов
    :return:
    """
    last_block_numbers_checked = get_local_last_blocks()
    while True:
        for bc in last_block_numbers_checked.keys():
            last_block_number = get_last_block_number(bc)
            if last_block_number > last_block_numbers_checked[bc]:
                results = check_filters(bc, last_block_numbers_checked[bc] + 1)
                if results:
                    print('results were found')
                    # target_addresses = [result['filter_target']['address'] for result in results]
                    models = get_objects_by_addresses()
                    for result in results:
                        for model in models:
                            if result['filter_target']['address'].lower() == model['address'].lower():
                                print(model['telegram_id'], result)
                                message = str(result)
                                send_message(message=message, chat_id=model['telegram_id'])
                print(bc, last_block_numbers_checked[bc] + 1)
                last_block_numbers_checked[bc] += 1
                set_local_last_blocks(last_block_numbers_checked)
        sleep(1)


if __name__ == '__main__':
    sync_transfers()

import json
from time import sleep

from watchdata import check_filters
from watchdata import get_last_block_number


def get_local_last_blocks():
    with open('last_blocks', 'r') as file:
        last_blocks = file.read()
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
                res = check_filters(bc, last_block_numbers_checked[bc] + 1)
                if res:
                    print(res)
                print(bc, last_block_numbers_checked[bc] + 1)
                last_block_numbers_checked[bc] += 1
                set_local_last_blocks(last_block_numbers_checked)
        sleep(1)


if __name__ == '__main__':
    sync_transfers()

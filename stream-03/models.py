import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def execute_raw_query(raw_query: str):
    sqlite_connection = None
    try:
        # todo: вынести создание коннекта отдельно, чтобы не создавать коннект на каждый запрос
        sqlite_connection = sqlite3.connect('sqlite_python.db')
        sqlite_connection.row_factory = dict_factory
        cursor = sqlite_connection.cursor()

        cursor.execute(raw_query)
        records = cursor.fetchall()
        sqlite_connection.commit()
        cursor.close()

        if records:
            return records

    except sqlite3.Error as error:
        print(f'Ошибка при подключении к sqlite: {error}')
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")

def create_addresses_table():
    """Создание таблицы с адресами"""
    sqlite_create_table_query = """CREATE TABLE addresses (
                                id INTEGER PRIMARY KEY,
                                telegram_id TEXT NOT NULL,
                                address TEXT NOT NULL,
                                blockchain TEXT NOT NULL,
                                name TEXT NOT NULL);"""
    execute_raw_query(sqlite_create_table_query)

def get_addresses_by_telegram_id(telegram_id: str):
    """Получение адресов по телеграм айди"""
    raw_query = f"""
        select * from addresses
        where telegram_id = {telegram_id}
    """
    return execute_raw_query(raw_query)

def insert_address(telegram_id: str, address: str, blockchain: str, name: str):
    raw_query = f"""
            insert into addresses(telegram_id, address, blockchain, name)
            VALUES('{telegram_id}', '{address}', '{blockchain}', '{name}')
        """
    return execute_raw_query(raw_query)

def delete_addresses(telegram_id: str, address: str, blockchain: str):
    raw_query = f"""
            delete from addresses 
            where telegram_id = '{telegram_id}'
            and address = '{address}' and blockchain = '{blockchain}'
    """
    execute_raw_query(raw_query)

def get_address_by_telegram_id_address_blockchain(telegram_id: str, address: str, blockchain: str):
    result = None
    raw_query = f"""
        select * from addresses
        where telegram_id = '{telegram_id}'
            and address = '{address}' and blockchain = '{blockchain}'
        limit 1 
    """
    res = execute_raw_query(raw_query)
    if res:
        result = res[0]
    return result


def get_objects_by_addresses():
    # todo: Добавить фильтр по адресам из результатов фильтров
    raw_query = f"""
    select * from addresses
    """
    res = execute_raw_query(raw_query)
    return res

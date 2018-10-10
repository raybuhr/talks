from collections import OrderedDict
import logging
import requests
import sqlite3
import time


def get_currency_data(source_currency: str, dest_currency: str):
    base_url = 'https://free.currencyconverterapi.com/api/v6/convert'
    exchange = f'{source_currency}_{dest_currency}'
    logging.info(f'getting data from {exchange}')
    resp = requests.get(base_url, params={'q': exchange})
    if not resp.ok:
        logging.info(f'request failed with error: {resp.reason}')
        return
    logging.info('success!')
    return resp.json()


def cleanup_data(currency_resp_data):
    logging.info('formatting HTTP response data')
    resp_values = list(currency_resp_data.get('results').values())[0]
    cleaned_data = OrderedDict()
    cleaned_data['source_currency'] = resp_values.get('fr')
    cleaned_data['dest_currency'] = resp_values.get('to')
    cleaned_data['exchange_rate'] = resp_values.get('val')
    cleaned_data['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    return cleaned_data


def create_db_table(db_cursor):
    logging.info('establishing db table...')
    query = '''CREATE TABLE IF NOT EXISTS exchange_rates (
        source_currency TEXT, dest_currency TEXT,
        exchange_rate REAL, time TEXT)'''
    db_cursor.execute(query)


def save_to_db(db_cursor, clean_data):
    logging.info('inserting cleaned HTTP data to db table')
    clean_data_values = tuple(clean_data.values())
    logging.info(f'clean data values: {clean_data_values}')
    db_cursor.execute(
        'INSERT INTO exchange_rates VALUES (?, ?, ?, ?)', clean_data_values)


def run_job():
    logging.basicConfig(filename='my_cool_script.log',
                        level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.info('connecting to db')
    con = sqlite3.connect('exchange_rates.db')
    cur = con.cursor()
    create_db_table(cur)
    raw_data = get_currency_data('USD', 'MXN')
    clean_data = cleanup_data(raw_data)
    save_to_db(cur, clean_data)
    con.commit()
    con.close()
    logging.info('completed job')


if __name__ == '__main__':
    run_job()

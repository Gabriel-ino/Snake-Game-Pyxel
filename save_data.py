import sqlite3 as sql
from atexit import register
from time import sleep

conn = sql.connect('save.db')
cursor = conn.cursor()


def create_table():
    cursor.execute('CREATE TABLE IF NOT EXISTS data(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT, '
                   'score REAL)')


def set_values(name: str, score: int):
    cursor.execute('INSERT INTO data(name,score) VALUES(?,?)', (name, score))


@register
def auto_save(name, score):
    print('Saving score', end='')
    for c in range(3):
        sleep(0.3)
        print('.', end='')

    set_values(name, score)

    conn.commit()

    print('Score saved!')



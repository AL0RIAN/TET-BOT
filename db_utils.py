import sqlite3
import os.path

# rows: user, command, date, hotels


def to_db(data: list) -> None:
    db_path = os.path.join(os.path.abspath("history.db"))

    con = sqlite3.connect(db_path, check_same_thread=False)
    cur = con.cursor()
    cur.execute("INSERT INTO history VALUES(?, ?, ?, ?)", data)
    con.commit()


def from_db(user_id: str) -> list:
    db_path = os.path.join(os.path.abspath("history.db"))

    con = sqlite3.connect(db_path, check_same_thread=False)
    cur = con.cursor()
    result = list()

    for row in cur.execute(f"SELECT command, date, hotels FROM history WHERE user = '{user_id}'"):
        result.append(row)
        print(f"\nInfo: {row} added")

    return result

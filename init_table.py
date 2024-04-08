import mysql.connector
from mysql.connector import Error
import threading
import datetime
import random
from dotenv import load_dotenv
import os

load_dotenv()


def create_users_batch(batch_size):
    batch = []
    for _ in range(batch_size):
        # Generate a random date within a reasonable range, e.g., 1900-01-01 to 2023-12-31
        start_date = datetime.date(1900, 1, 1)
        end_date = datetime.date(2023, 12, 31)
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + datetime.timedelta(days=random_number_of_days)

        batch.append((random_date,))
    return batch


def insert_batch(connection, batch):
    try:
        cursor = connection.cursor()
        query = 'INSERT INTO user (birthday) VALUES (%s)'
        cursor.executemany(query, batch)
        connection.commit()
        print(f'Batch inserted successfully. Batch size: {len(batch)}')
    except Error as e:
        print(f'Error: {e}')
    finally:
        cursor.close()


def thread_task(total_users, batch_size, connection):
    try:
        if connection.is_connected():
            for _ in range(int(total_users / batch_size)):
                batch = create_users_batch(batch_size)
                insert_batch(connection, batch)
    except Error as e:
        print(f'Error while connecting to MariaDB: {e}')
    finally:
        if connection.is_connected():
            connection.close()


def main():
    total_users = 40000000  # 40 million users
    batch_size = 10000
    num_threads = 10
    users_per_thread = total_users // num_threads

    # Create a connection to the database
    connection = mysql.connector.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_DATABASE')
    )

    create_users_table = """
    CREATE TABLE IF NOT EXISTS user (
        id INT AUTO_INCREMENT,
        birthday DATE NOT NULL,
        PRIMARY KEY (id)
    );
    """
    cursor = connection.cursor()
    cursor.execute(create_users_table)
    connection.commit()
    cursor.close()

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=thread_task, args=(users_per_thread, batch_size, connection))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print('All data inserted.')

    if connection.is_connected():
        connection.close()


if __name__ == '__main__':
    main()

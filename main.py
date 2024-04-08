import mysql.connector
import datetime
import time
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()


def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Execution time: {end_time - start_time} seconds \n")
        return result

    return wrapper


@timer_decorator
def get_users_by_exact_birthday(connection, birthday):
    try:
        cursor = connection.cursor()
        query = " SELECT SQL_NO_CACHE * FROM user WHERE birthday = %s"
        formatted_query = query % birthday
        print(formatted_query)
        cursor.execute(query, (birthday,))
        return cursor.fetchall()
    finally:
        cursor.close()


@timer_decorator
def get_users_by_month(connection, month):
    try:
        cursor = connection.cursor()
        query = " SELECT SQL_NO_CACHE * FROM user WHERE MONTH(birthday) = %s"
        formatted_query = query % month
        print(formatted_query)
        cursor.execute(query, (month,))
        return cursor.fetchall()
    finally:
        cursor.close()


@timer_decorator
def get_users_by_year(connection, year):
    try:
        cursor = connection.cursor()
        query = " SELECT SQL_NO_CACHE * FROM user WHERE YEAR(birthday) = %s"
        formatted_query = query % year
        print(formatted_query)
        cursor.execute(query, (year,))
        return cursor.fetchall()
    finally:
        cursor.close()


@timer_decorator
def get_users_by_age(connection, age):
    try:
        cursor = connection.cursor()
        query = " SELECT SQL_NO_CACHE * FROM user WHERE YEAR(CURDATE()) - YEAR(birthday) = %s"
        formatted_query = query % age
        print(formatted_query)
        cursor.execute(query, (age,))
        return cursor.fetchall()
    finally:
        cursor.close()


@timer_decorator
def get_users_by_date_range(connection, start_date, end_date):
    try:
        cursor = connection.cursor()
        query = " SELECT SQL_NO_CACHE * FROM user WHERE birthday BETWEEN %s AND %s"
        formatted_query = query % (start_date, end_date)
        print(formatted_query)
        cursor.execute(query, (start_date, end_date))
        return cursor.fetchall()
    finally:
        cursor.close()


def create_btree_index(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE INDEX idx_birthday ON user(birthday)")
        connection.commit()
        print("Index created successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()


def create_hash_index(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE INDEX idx_birthday ON user(birthday) USING HASH")
        connection.commit()
        print("Index created successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()


def drop_index_by_name(connection, index_name):
    try:
        cursor = connection.cursor()
        cursor.execute(f"DROP INDEX {index_name} ON user")
        connection.commit()
        print("Index dropped successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()


if __name__ == "__main__":
    connection = mysql.connector.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_DATABASE')
    )
    get_users_by_exact_birthday(connection, datetime.date(2022, 1, 1))
    get_users_by_month(connection, 1)
    get_users_by_year(connection, 2001)
    get_users_by_age(connection, 30)
    get_users_by_date_range(connection, datetime.date(1990, 1, 1), datetime.date(2023, 12, 31))
    # create_btree_index(connection)
    # drop_index_by_name(connection, "idx_birthday")
    # create_hash_index(connection)
    connection.close()

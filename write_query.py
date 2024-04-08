import mysql.connector
import threading
import queue
import time
import datetime
import random
from dotenv import load_dotenv
import os

load_dotenv()

insert_query = 'INSERT INTO user (birthday) VALUES (%s);'


def worker(work_queue, counter_lock, insert_counter):
    connection = mysql.connector.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_DATABASE')
    )
    cursor = connection.cursor()

    while True:
        try:
            birthday = work_queue.get(timeout=1)  # Adjust timeout as needed

            # Execute the insert query
            cursor.execute(insert_query, (birthday,))
            connection.commit()

            # Increment the counter safely
            with counter_lock:
                insert_counter[0] += 1

        except queue.Empty:
            continue

    cursor.close()
    connection.close()


def generate_dummy_birthday():
    start_date = datetime.date(1900, 1, 1)
    end_date = datetime.date(2023, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return random_date


def data_feeder(work_queue):
    while True:
        work_queue.put(generate_dummy_birthday())


def monitor_qps(counter_lock, insert_counter, qps_list):
    while True:
        time.sleep(1)  # Check every second
        with counter_lock:
            current_qps = insert_counter[0]
            qps_list.append(current_qps)  # Add current QPS to the list
            average_qps = sum(qps_list) / len(qps_list)
            print(f'Current QPS: {current_qps}, Average QPS: {average_qps:.2f}')
            insert_counter[0] = 0  # Reset counter for the next second


def main():
    num_threads = 10
    work_queue = queue.Queue(maxsize=1000)

    insert_counter = [0]
    qps_list = []
    counter_lock = threading.Lock()

    feeder_thread = threading.Thread(target=data_feeder, args=(work_queue,))
    feeder_thread.daemon = True
    feeder_thread.start()

    # Start worker threads
    for _ in range(num_threads):
        thread = threading.Thread(target=worker, args=(work_queue, counter_lock, insert_counter))
        thread.daemon = True
        thread.start()

    monitor_thread = threading.Thread(target=monitor_qps, args=(counter_lock, insert_counter, qps_list))
    monitor_thread.daemon = True
    monitor_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping...')


if __name__ == '__main__':
    main()

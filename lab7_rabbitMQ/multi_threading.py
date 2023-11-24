import concurrent.futures
import producer
import receiver

def main():
    threads = 10
    workers = 10

    producer.main()

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        for i in range(workers):
            executor.submit(receiver.main)

if __name__ == '__main__':
    main()


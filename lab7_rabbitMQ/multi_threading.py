import concurrent.futures
import producer
import receiver

def main():
    threads = 100
    workers = 100

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.submit(producer.main)
        for i in range(workers):
            executor.submit(receiver.main)

if __name__ == '__main__':
    main()


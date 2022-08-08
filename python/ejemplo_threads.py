from threading import Thread
from time import perf_counter

def replace(filename, substr, new_substr):
    print(f'Processing the file {filename} with {substr} and {new_substr}')

def main():
    filenames = [
        'c:/temp/test1.txt',
        'c:/temp/test2.txt',
        'c:/temp/test3.txt',
        'c:/temp/test4.txt',
        'c:/temp/test5.txt',
        'c:/temp/test6.txt',
        'c:/temp/test7.txt',
        'c:/temp/test8.txt',
        'c:/temp/test9.txt',
        'c:/temp/test10.txt',
    ]

    # create and start 10 threads
    threads = []
    for n in range(1, 8):
        t = Thread(target=replace, args=(filenames[n], 'id', 'new_id'))
        threads.append(t)

    # start the threads
    for thread in threads:
        thread.start()

    # wait for the threads to complete
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    start_time = perf_counter()

    main()

    end_time = perf_counter()
    print(f'It took {end_time- start_time :0.2f} second(s) to complete.')

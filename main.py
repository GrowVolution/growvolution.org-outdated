from LIBRARY import *
from watcher import start_watcher, stop_watcher, reload_dotenv

load_dotenv()
env = os.environ.copy()
env['INSTANCE'] = 'main'
mode = env['EXEC_MODE']

logs_dir = Path(__file__).parent / 'logs'
logs_dir.mkdir(parents=True, exist_ok=True)
main_proc = None
watcher = None


def start_main():
    global main_proc
    timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
    logfile = logs_dir / f"{timestamp}.log"
    main_proc = subprocess.Popen(
        ['gunicorn', 'app:APP', '-b', '127.0.0.1:5000', '-k', 'eventlet'],
        env=env,
        stdout=open(logfile, 'w'),
        stderr=subprocess.STDOUT
    )


def start_watch():
    global watcher
    watcher = start_watcher()


def stop_watch():
    global watcher
    watcher = stop_watcher(watcher) if watcher else None


def restart_main():
    if main_proc:
        main_proc.terminate()
        main_proc.wait()
    start_main()


start_main()


if mode == 'DEBUG':
    print("\n\nGrowVolution 2025 - GNU General Public License")
    print("Server Control Script: Enter the number of the action you want to perform.\n")

    print('1 - start debug')
    print('2 - stop debug')
    print('3 - debug to main')
    print('4 - reload .env')
    print('5 - exit')

    while True:
        cmd = input('> ')
        if cmd == '1':
            start_watch()

        elif cmd == '2':
            stop_watch()

        elif cmd == '3':
            restart_main()

        elif cmd == '4':
            reload_dotenv()
            if watcher:
                stop_watch()
                start_watch()

            load_dotenv()
            env = os.environ.copy()
            env['INSTANCE'] = 'main'
            restart_main()

        elif cmd == '5':
            stop_watch()
            if main_proc:
                main_proc.terminate()
            break

        else:
            print('Unknown command!')

    print("\nThank you for playing the game of life, bye!")

else:
    main_proc.wait()

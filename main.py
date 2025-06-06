from watcher import start_watcher, stop_watcher, reload_dotenv
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from types import FrameType
import os, subprocess, signal

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


def restart_main(reload: bool = False):
    if main_proc and reload:
        main_proc.send_signal(signal.SIGHUP)

    elif main_proc:
        main_proc.terminate()
        main_proc.wait()
        start_main()

    else:
        start_main()


def update_database():
    msg = input("Enter migration message: ").strip()
    if not msg:
        print("Abgebrochen – keine Nachricht eingegeben.\n")
        return

    db_env = os.environ.copy()
    db_env['FLASK_APP'] = 'db_manage.py'
    subprocess.run(["flask", "db", "migrate", "-m", msg], env=db_env)
    subprocess.run(["flask", "db", "upgrade"], env=db_env)
    print()


def _shutdown(signum: int, frame: FrameType | None):
    print(f"Handling signal {'SIGTERM' if signum == signal.SIGTERM else 'SIGINT'}, server will shutdown now...")
    shutdown()
    print("Shutdown complete! Thank you for playing the game of life.")


def shutdown():
    stop_watch()
    if main_proc:
        main_proc.terminate()


start_main()
signal.signal(signal.SIGINT, _shutdown)
signal.signal(signal.SIGTERM, _shutdown)


def start_message():
    print("\n\nGrowVolution 2025 - GNU General Public License")
    print("Server Control Script: Enter the number of the action you want to perform.\n")

    print('1 - start debug')
    print('2 - stop debug')
    print('3 - debug to main')
    print('4 - reload .env')
    print('5 - update database')
    print('6 - restart main')
    print('7 - clear console')
    print('8 - exit')


if mode == 'DEBUG':
    start_message()

    while True:
        cmd = input('> ')
        if cmd == '1':
            start_watch()

        elif cmd == '2':
            stop_watch()

        elif cmd == '3':
            restart_main(True)

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
            update_database()

        elif cmd == '6':
            restart_main()

        elif cmd == '7':
            os.system('cls' if os.name == 'nt' else 'clear')
            start_message()

        elif cmd == '8':
            shutdown()
            break

        else:
            print('Unknown command!')

    print("\nThank you for playing the game of life, bye!")

else:
    main_proc.wait()

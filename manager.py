import psutil # Used to check if game profile is running
import time # Used to delay between launching accounts
import subprocess # Used to launch devious launcher and detach from game clients from parent process

# Example account row: username|password|runeliteprofile|proxy:port:username:password
DEVIOUS_LAUNCHER_PATH = "./client.jar" # Launcher path
ACCOUNTS_PATH = "./accounts.txt" # Launcher path
LAUNCH_DELAY=15 # Delay between launching accounts

# Parse account row into username, password, runelite profile, and proxy
def parse_account(account):
    username = account.split("|")[0]
    password = account.split("|")[1]
    runelite_profile = account.split("|")[2]
    proxy = account.split("|")[3]
    return username, password, runelite_profile, proxy

# Check if game profile is running by checking if the profile is in the command line arguments of the java process
def is_game_profile_process_running(profile):
    for process in psutil.process_iter(attrs=['pid', 'cmdline']):
        try:
            cmd_line = process.info['cmdline']
            #uncomment below to debug cmd_line
            #if cmd_line and 'java' in cmd_line[0]:
                #print(cmd_line)
            if cmd_line and f'--username={profile}' in cmd_line and 'java' in cmd_line[0]:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    print(f"Profile {profile} is not running")

# Launch game profile with devious launcher
def launch_game(account):
    # Parse account
    username, password, runelite_profile, proxy = parse_account(account)
    if is_game_profile_process_running(username):
        print(f"Account {username} is already running. Skipping...")
        return
    print(f"Launching {username} on proxy {proxy} with profile {runelite_profile}")
    #if proxy is not empty, add proxy to java arguments
    if proxy!="":
        try:
            return subprocess.Popen(["java", "-jar", DEVIOUS_LAUNCHER_PATH, # devious launcher path
                                 f"--config={runelite_profile}", # runelite profile
                                 f"--username={username}", # username
                                 f"--proxy={proxy}",
                                 f"--password={password}"],
                                 stdout=subprocess.DEVNULL, # Redirect stdout to nullto prevent spam
                                 )
        except Exception as e:
            print(f"Failed to launch {username}: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)
            return launch_game(account)
    else:
        try:
            return subprocess.Popen(["java", "-jar", DEVIOUS_LAUNCHER_PATH, # devious launcher path
                                 f"--config={runelite_profile}", # Runelite profile
                                 f"--username={username}", # username
                                 f"--password={password}",
                                 f"--scale=.5"],
                                 stdout=subprocess.DEVNULL, # Redirect stdout to nullto prevent spam
                                 )
        except Exception as e:
            print(f"Failed to launch {username}: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)
            return launch_game(account)

# Read accounts from file in the format of username|username|runeliteprofile|proxy:port:username:password
def read_accounts_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

# Monitor processes and relaunch crashed processes
def monitor_processes():
    accounts = read_accounts_from_file(ACCOUNTS_PATH)
    print(f"Loading {len(accounts)} accounts...")
    processes = [None] * len(accounts)
    
    for i, account in enumerate(accounts):
        processes[i] = launch_game(account)
        time.sleep(LAUNCH_DELAY)


    while True:
        for i, account in enumerate(accounts):
            username, password, runelite_profile, proxy = parse_account(account)
            if not is_game_profile_process_running(username):
                print(f"{username} crashed! Relaunching...")
                processes[i] = launch_game(account)
                time.sleep(LAUNCH_DELAY)

        time.sleep(15)

monitor_processes()
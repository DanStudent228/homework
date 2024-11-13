import configparser
import tarfile
import time
import calendar
from datetime import datetime
import xml.etree.ElementTree as ET

config = configparser.ConfigParser()
config.read('config.ini')

vfs_path = config['Paths']['vfs_archive']
log_path = config['Paths']['log_file']
startup_script = config['Paths']['startup_script']

vfs_archive = tarfile.open(vfs_path, 'r')

vfs_structure = {}

for member in vfs_archive.getmembers():
    vfs_structure[member.name] = member
    
def cmd_ls(current_dir):
    contents = [name for name in vfs_structure.keys() if name.startswith(current_dir) and name != current_dir]
    for item in contents:
        print(item.replace(current_dir, '').split('/')[0])

def cmd_cd(path, current_dir):
    new_path = os.path.normpath(os.path.join(current_dir, path))
    if new_path in vfs_structure or any(k.startswith(new_path + '/') for k in vfs_structure):
        return new_path
    else:
        print("Нет такого файла или директории")
        return current_dir

def cmd_exit():
    print("Выход из эмулятора.")
    exit()

start_time = time.time()

def cmd_uptime():
    uptime = time.time() - start_time
    hours, rem = divmod(uptime, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"Время работы: {int(hours)} часов, {int(minutes)} минут, {int(seconds)} секунд")

def cmd_cal():
    now = datetime.now()
    cal = calendar.month(now.year, now.month)
    print(cal)

log_root = ET.Element('Session')

def log_action(command):
    action = ET.SubElement(log_root, 'Action')
    action.text = command

def save_log():
    tree = ET.ElementTree(log_root)
    tree.write(log_path)

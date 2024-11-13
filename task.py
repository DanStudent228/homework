import configparser
import tarfile
import time
import calendar
from datetime import datetime
import xml.etree.ElementTree as ET
import calendar
import os
from pathlib import PurePosixPath
import logging
import atexit

class XMLFileHandler(logging.Handler):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.root = ET.Element('Logs')  # Корневой элемент XML

    def emit(self, record):
        # Создаём новый элемент LogEntry для каждой записи лога
        log_entry = ET.SubElement(self.root, 'LogEntry')
        timestamp = datetime.fromtimestamp(record.created).isoformat()
        ET.SubElement(log_entry, 'Timestamp').text = timestamp
        ET.SubElement(log_entry, 'Level').text = record.levelname
        ET.SubElement(log_entry, 'Message').text = record.getMessage()

    def close(self):
        # Сохраняем XML-лог в файл при закрытии обработчика
        tree = ET.ElementTree(self.root)
        tree.write(self.filename, encoding='utf-8', xml_declaration=True)
        super().close()
    
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
    
    # Создание стандартного файлового обработчика для текстового лога
file_handler = logging.FileHandler('emulator.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
    
    # Создание XML обработчика
xml_handler = XMLFileHandler('log.xml')
xml_handler.setLevel(logging.DEBUG)  
logger.addHandler(xml_handler)

    # Регистрация функции закрытия обработчиков при завершении программы
def close_handlers():
    xml_handler.close()

atexit.register(close_handlers)

    # Функция для нормализации пути
def normalize_path(path):
    parts = path.split('/')
    stack = []
    for part in parts:
        if part == '..':
            if stack:
                stack.pop()
        elif part == '.' or part == '':
            continue
        else:
            stack.append(part)
    return '/' + '/'.join(stack)
def cmd_ls(current_dir, vfs_structure):
    items = set()
    current_dir = current_dir.rstrip('/')
    logging.debug(f"cmd_ls called with current_dir='{current_dir}'")
    for path in vfs_structure.keys():
        if path == current_dir:
            continue
        if current_dir == '/':
            if path.startswith('/') and path.count('/') == 1:
                top_level = path[1:]
                if top_level:
                    items.add(top_level)
                    logging.debug(f"Добавлен элемент: {top_level}")
        else:
            if path.startswith(current_dir + '/'):
                relative_path = path[len(current_dir) + 1:]
                if '/' in relative_path:
                    top_level = relative_path.split('/')[0]
                else:
                    top_level = relative_path
                if top_level:
                    items.add(top_level)
                    logging.debug(f"Добавлен элемент: {top_level}")
    sorted_items = sorted(items)
    logging.info(f"Содержимое {current_dir}: {', '.join(sorted_items)}")
    return sorted_items

def cmd_cd(path, current_dir, vfs_structure):
    # Используем PurePosixPath для корректного формирования путей
    current = PurePosixPath(current_dir)
    new_path = (current / path).as_posix()
    new_path = normalize_path(new_path)
    logging.debug(f"cmd_cd called with path='{path}', current_dir='{current_dir}', new_path='{new_path}'")
    if new_path in vfs_structure and vfs_structure[new_path] is None:
        logging.info(f"Переход в {new_path} успешен")
        return new_path
    else:
        logging.error("Нет такого файла или директории")
        return current_dir

def cmd_exit():
    logging.info("Выход из эмулятора.")
    exit()

start_time = time.time()

def cmd_uptime():
    uptime = time.time() - start_time
    hours, rem = divmod(uptime, 3600)
    minutes, seconds = divmod(rem, 60)
    result = f"Время работы: {int(hours)} часов, {int(minutes)} минут, {int(seconds)} секунд"
    logging.info(result)
    return result

def cmd_cal():
    now = datetime.now()
    cal = calendar.month(now.year, now.month)
    logging.info(f"Текущий месяц:\n{cal}")
    return cal

# Функция обработки команд
def process_command(command, current_dir, vfs_structure, log_path):
    parts = command.split()
    if not parts:
        return current_dir
    cmd = parts[0]
    args = parts[1:] if len(parts) > 1 else []

    if cmd == 'ls':
        items = cmd_ls(current_dir, vfs_structure)
        print('  '.join(items))
    elif cmd == 'cd':
        if args:
            return cmd_cd(args[0], current_dir, vfs_structure)
        else:
            logging.error("Не указана директория")
    elif cmd == 'exit':
        cmd_exit()
    elif cmd == 'uptime':
        cmd_uptime()
    elif cmd == 'cal':
        cal_output = cmd_cal()
        print(cal_output)
    else:
        logging.error("Команда не найдена")
    return current_dir
    
def execute_startup_script(vfs_structure, log_path, startup_script):
    try:
        with open(startup_script, 'r', encoding='utf-8') as script:
            for line in script:
                command = line.strip()
                if command:
                    process_command(command, '/', vfs_structure, log_path)
    except FileNotFoundError:
        logging.error(f"Ошибка: Стартовый скрипт {startup_script} не найден.")
    except Exception as e:
        logging.error(f"Ошибка при выполнении стартового скрипта: {e}")

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    vfs_path = config['Paths']['vfs_archive']
    log_path = config['Paths']['log_file']
    startup_script = config['Paths']['startup_script']

    # Проверка существования и размера файла vfs.tar
    if not os.path.exists(vfs_path):
        logging.error(f"Файл виртуальной файловой системы {vfs_path} не найден.")
        exit(1)

    if os.path.getsize(vfs_path) == 0:
        logging.error(f"Файл виртуальной файловой системы {vfs_path} пустой.")
        exit(1)

    try:
        vfs_archive = tarfile.open(vfs_path, 'r')
    except tarfile.ReadError as e:
        logging.error(f"Ошибка при открытии tar-архива: {e}")
        exit(1)

    # Создаём словарь для представления файловой системы
    vfs_structure = {}

    for member in vfs_archive.getmembers():
        path = member.name
        if path.startswith('vfs/'):
            path = '/' + path[len('vfs/'):]
        else:
            path = '/' + path
        if member.isdir():
            vfs_structure[path] = None
        else:
            vfs_structure[path] = member

    execute_startup_script(vfs_structure, log_path, startup_script)

    current_dir = '/'
    while True:
        try:
            command = input(f'{current_dir}> ')
            current_dir = process_command(command, current_dir, vfs_structure, log_path)
        except EOFError:
            # Обработка Ctrl+D или EOF
            logging.info("Выход из эмулятора (EOF).")
            logging.info(cmd_uptime())
            exit()
        except KeyboardInterrupt:
            # Обработка Ctrl+C
            logging.info("Выход из эмулятора (KeyboardInterrupt).")
            logging.info(cmd_uptime())
            exit()
        except Exception as e:
            logging.error(f"Произошла ошибка: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
import configparser
import tarfile

config = configparser.ConfigParser()
config.read('config.ini')

vfs_path = config['Paths']['vfs_archive']
log_path = config['Paths']['log_file']
startup_script = config['Paths']['startup_script']

vfs_archive = tarfile.open(vfs_path, 'r')

vfs_structure = {}

for member in vfs_archive.getmembers():
    vfs_structure[member.name] = member
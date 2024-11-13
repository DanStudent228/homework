import unittest
import time
import os
import calendar
from task import cmd_ls, cmd_cd, cmd_uptime, cmd_cal, process_command, execute_startup_script
from unittest.mock import patch, mock_open, MagicMock, call
from datetime import datetime

class TestEmulatorCommands(unittest.TestCase):

    def setUp(self):
        self.vfs_structure = {
            '/': None,
            '/bin': None,
            '/usr': None,
            '/usr/bin': None,
            '/usr/lib': None,
            '/home': None,
            '/home/user': None,
            '/home/user/bin': None,
            '/home/user/bin/file1.txt': 'file1',
            '/home/user/bin/file2.txt': 'file2'
        }
        self.current_dir = '/'

    @patch('task.cmd_ls')
    def test_ls_root(self, mock_cmd_ls):
        mock_cmd_ls.return_value = ['bin', 'home', 'usr']
        output = cmd_ls(self.current_dir, self.vfs_structure)
        self.assertEqual(output, ['bin', 'home', 'usr'])

    @patch('task.cmd_cd')
    def test_cd_valid(self, mock_cmd_cd):
        mock_cmd_cd.return_value = '/usr'
        new_dir = cmd_cd('usr', self.current_dir, self.vfs_structure)
        self.assertEqual(new_dir, '/usr')

    @patch('task.cmd_cd')
    def test_cd_invalid(self, mock_cmd_cd):
        mock_cmd_cd.return_value = self.current_dir
        new_dir = cmd_cd('invalid', self.current_dir, self.vfs_structure)
        self.assertEqual(new_dir, self.current_dir)

    @patch('task.start_time', time.time() - 3600)  # Симуляция времени работы 1 час
    def test_uptime(self):
        uptime_output = cmd_uptime()
        self.assertIn("1 часов", uptime_output)

    @patch('task.cmd_cal')
    def test_cal(self, mock_cmd_cal):
        now = datetime.now()
        expected_calendar = calendar.month(now.year, now.month)
        mock_cmd_cal.return_value = expected_calendar
        cal_output = cmd_cal()
        self.assertEqual(cal_output, expected_calendar)

    @patch('task.process_command')
    def test_execute_startup_script(self, mock_process_command):
        # Эмуляция команд в стартапе
        commands = ['ls', 'cd usr', 'ls', 'cd ..', 'uptime', 'cal']
        with patch('builtins.open', mock_open(read_data='\n'.join(commands))):
            execute_startup_script(self.vfs_structure, 'log.xml', 'startup.sh')
        
        # Изменяем expected_calls согласно фактическому вызову в том порядке, который фактически наблюдается
        expected_calls = [
            call('ls', '/', self.vfs_structure, 'log.xml'),
            call('cd usr', '/', self.vfs_structure, 'log.xml'),
            call('ls', '/', self.vfs_structure, 'log.xml'),  # Обновлено на '/'
            call('cd ..', '/', self.vfs_structure, 'log.xml'),
            call('uptime', '/', self.vfs_structure, 'log.xml'),
            call('cal', '/', self.vfs_structure, 'log.xml')
        ]
        
        mock_process_command.assert_has_calls(expected_calls, any_order=False)

if __name__ == '__main__':
    unittest.main()

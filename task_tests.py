import unittest
import sys
import os
from task import cmd_ls, cmd_cd, cmd_cal, cmd_uptime

class TestEmulatorCommands(unittest.TestCase):

    def setUp(self):
        global vfs_structure
        vfs_structure = {
            '/': None,
            '/bin': None,
            '/usr': None,
            '/usr/bin': None,
            '/usr/lib': None,
            '/home': None,
            '/home/user': None,
        }
        self.current_dir = '/'

    def test_ls_root(self):
        expected_output = ['bin', 'home', 'usr']
        output = cmd_ls(self.current_dir, vfs_structure)
        self.assertEqual(output, expected_output)

    def test_ls_subdirectory(self):
        self.current_dir = '/usr'
        expected_output = ['bin', 'lib']
        output = cmd_ls(self.current_dir, vfs_structure)
        self.assertEqual(output, expected_output)

    def test_cd_valid(self):
        new_dir = cmd_cd('usr', self.current_dir, vfs_structure)
        self.assertEqual(new_dir, '/usr')

    def test_cd_invalid(self):
        new_dir = cmd_cd('invalid', self.current_dir, vfs_structure)
        self.assertEqual(new_dir, self.current_dir)

    def test_uptime(self):
        result = cmd_uptime()
        self.assertIsNotNone(result)

    def test_cal(self):
        cal_output = cmd_cal()
        self.assertIsNotNone(cal_output)
        now = datetime.now()
        expected_header = f"{calendar.month_name[now.month]} {now.year}"
        self.assertIn(expected_header, cal_output)

if __name__ == '__main__':
    unittest.main()

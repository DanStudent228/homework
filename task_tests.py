import unittest

class TestEmulatorCommands(unittest.TestCase):

    def setUp(self):
        # Инициализация перед каждым тестом
        self.current_dir = '/'

    def test_ls_root(self):
        # Тест команды ls в корневой директории
        expected_output = ['bin', 'usr', 'home']
        output = cmd_ls(self.current_dir)
        self.assertEqual(output, expected_output)

    def test_ls_subdirectory(self):
        # Тест команды ls в поддиректории
        self.current_dir = '/usr'
        expected_output = ['bin', 'lib']
        output = cmd_ls(self.current_dir)
        self.assertEqual(output, expected_output)

    def test_cd_valid(self):
        # Тест команды cd с существующей директорией
        new_dir = cmd_cd('usr', self.current_dir)
        self.assertEqual(new_dir, '/usr')

    def test_cd_invalid(self):
        # Тест команды cd с несуществующей директорией
        new_dir = cmd_cd('invalid', self.current_dir)
        self.assertEqual(new_dir, self.current_dir)

    def test_uptime(self):
        # Тест команды uptime
        # Здесь можно проверить формат вывода или просто выполнение без ошибок
        cmd_uptime()

    def test_cal(self):
        # Тест команды cal
        # Проверяем, что выводится не пустой календарь
        cal_output = cmd_cal()
        self.assertIsNotNone(cal_output)

if __name__ == '__main__':
    unittest.main()

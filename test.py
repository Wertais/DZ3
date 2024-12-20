import unittest
from unittest.mock import mock_open, patch
from main import ConfigParser

class TestConfigParser(unittest.TestCase):

    # Устанавливаем начальные данные перед каждым тестом
    def setUp(self):
        self.parser = ConfigParser()

    # Тест проверяет, что обработка отсутствующего файла работает корректно
    def test_file_not_found(self):
        self.parser.parse_file("nonexistent_file.txt")
        self.assertIn("Файл 'nonexistent_file.txt' не найден.", self.parser.errors)

    # Тест проверяет корректность парсинга переменной и её добавление в словарь
    @patch("builtins.open", new_callable=mock_open, read_data="var x := 5;\n")
    def test_valid_variable_declaration(self, mock_file):
        self.parser.parse_file("dummy_file.txt")
        self.assertIn("x", self.parser.variables)
        self.assertEqual(self.parser.variables["x"], 5)

    # Тест проверяет корректность парсинга словаря и выявление ошибок при некорректных значениях
    @patch("builtins.open", new_callable=mock_open, read_data="begin\na: 10;\nb: 20.5;\nend\n")
    def test_dictionary_parsing(self, mock_file):
        self.parser.parse_file("dummy_file.txt")
        self.assertEqual(len(self.parser.dictionaries), 1)
        self.assertEqual(self.parser.dictionaries[0], {"a": 10, "b": 20.5})

    # Тест проверяет обработку строки с некорректным значением в словаре
    @patch("builtins.open", new_callable=mock_open, read_data="begin\na: invalid;\nend\n")
    def test_dictionary_parsing_with_invalid_value(self, mock_file):
        self.parser.parse_file("dummy_file.txt")
        self.assertIn("Строка 2: некорректное значение 'invalid' в словаре.", self.parser.errors)

    # Тест проверяет обработку выражений с отсутствующими переменными и валидацию ошибок
    @patch("builtins.open", new_callable=mock_open, read_data="var y := x + 10;\n")
    def test_expression_evaluation_with_missing_variable(self, mock_file):
        self.parser.parse_file("dummy_file.txt")
        self.assertIn("Строка 1: ошибка вычисления выражения 'x + 10': name 'x' is not defined", self.parser.errors)

    # Тест проверяет удаление многострочных комментариев и корректное выполнение парсинга переменной
    @patch("builtins.open", new_callable=mock_open, read_data="<# комментарий #>\nvar z := 15;\n")
    def test_multiline_comment_removal(self, mock_file):
        self.parser.parse_file("dummy_file.txt")
        self.assertIn("z", self.parser.variables)
        self.assertEqual(self.parser.variables["z"], 15)

    # Тест проверяет корректность обработки 'end' без соответствующего 'begin'
    @patch("builtins.open", new_callable=mock_open, read_data="begin\nend\nend\n")
    def test_unmatched_end(self, mock_file):
        self.parser.parse_file("dummy_file.txt")
        self.assertIn("Строка 3: 'end' без соответствующего 'begin'.", self.parser.errors)

if __name__ == "__main__":
    unittest.main()

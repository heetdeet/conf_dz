import unittest
import tempfile
import os
import sys
from io import StringIO
from src.config_parser import ConfigParser, XMLGenerator, pretty_xml

"""
Unit-тесты для конфигурационного парсера
"""

class TestConfigParser(unittest.TestCase):
    """Тесты парсера конфигурационного языка"""
    
    def setUp(self):
        self.parser = ConfigParser()
    
    def test_parse_hex_number(self):
        """Парсинг шестнадцатеричного числа"""
        result = self.parser.parse("0x1A")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "number")
        self.assertEqual(result[0]["value"], 26)
    
    def test_parse_string(self):
        """Парсинг строки"""
        result = self.parser.parse('"Hello, World!"')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "string")
        self.assertEqual(result[0]["value"], "Hello, World!")
    
    def test_parse_array(self):
        """Парсинг массива"""
        result = self.parser.parse('list(0x0A, "test", 0xFF)')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "array")
        self.assertEqual(len(result[0]["values"]), 3)
    
    def test_parse_declaration(self):
        """Парсинг объявления константы"""
        result = self.parser.parse('def max_value := 0x64;')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "decl")
        self.assertEqual(result[0]["name"], "max_value")
    
    def test_parse_substitution(self):
        """Парсинг подстановки"""
        text = """
        def limit := 0x64;
        $[limit]
        """
        result = self.parser.parse(text)
        self.assertEqual(len(result), 2)
        # второй элемент должен быть числом (подстановка)
        self.assertEqual(result[1]["type"], "number")
        self.assertEqual(result[1]["value"], 100)
    
    def test_parse_complex_structure(self):
        """Парсинг сложной структуры"""
        text = """
        def timeout := 0x3E8;
        def server := "localhost";
        list($[timeout], $[server], 0x01)
        """
        result = self.parser.parse(text)
        self.assertEqual(len(result), 3)
    
    def test_parse_with_comment(self):
        """Парсинг с комментариями"""
        text = """
        -  Это комментарий
        0x1A  -  Число после комментария
        """
        result = self.parser.parse(text)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "number")
    
    def test_error_invalid_hex(self):
        """Ошибка при некорректном шестнадцатеричном числе"""
        with self.assertRaises(ValueError) as context:
            self.parser.parse("0x1G")
        self.assertTrue(isinstance(context.exception, ValueError))
    
    def test_error_unknown_constant(self):
        """Ошибка при использовании неизвестной константы"""
        with self.assertRaises(ValueError) as context:
            self.parser.parse("$[unknown]")
        self.assertIn("Неизвестная константа", str(context.exception))
    
    def test_error_syntax_missing_semicolon(self):
        """Ошибка при отсутствии точки с запятой"""
        with self.assertRaises(ValueError) as context:
            self.parser.parse("def x := 0x10")
        self.assertIn("Синтаксическая ошибка", str(context.exception))
    
    def test_error_unexpected_token(self):
        """Ошибка при неожиданном токене"""
        with self.assertRaises(ValueError) as context:
            self.parser.parse(")")
        self.assertTrue(isinstance(context.exception, ValueError))
    
    def test_error_lexical_invalid_char(self):
        """Лексическая ошибка при недопустимом символе"""
        with self.assertRaises(ValueError) as context:
            self.parser.parse("0x10 @ 0x20")
        self.assertIn("Лексическая ошибка", str(context.exception))
    
    def test_nested_array(self):
        """Парсинг вложенного массива"""
        result = self.parser.parse('list(list(0x01, 0x02), "test")')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "array")
        self.assertEqual(result[0]["values"][0]["type"], "array")


class TestXMLGenerator(unittest.TestCase):
    """Тесты генератора XML"""
    
    def test_generate_number(self):
        """Генерация XML для числа"""
        data = [{"type": "number", "value": 26, "original": "0x1A"}]
        xml_root = XMLGenerator.generate(data)
        
        self.assertEqual(xml_root.tag, "configuration")
        number_elem = xml_root.find("number")
        self.assertIsNotNone(number_elem)
        self.assertEqual(number_elem.text, "26")
        self.assertEqual(number_elem.get("hex"), "0x1A")
    
    def test_generate_string(self):
        """Генерация XML для строки"""
        data = [{"type": "string", "value": "test"}]
        xml_root = XMLGenerator.generate(data)
        
        string_elem = xml_root.find("string")
        self.assertIsNotNone(string_elem)
        self.assertEqual(string_elem.text, "test")
    
    def test_generate_array(self):
        """Генерация XML для массива"""
        data = [{"type": "array", "values": [
            {"type": "number", "value": 1, "original": "0x01"},
            {"type": "string", "value": "item"}
        ]}]
        
        xml_root = XMLGenerator.generate(data)
        array_elem = xml_root.find("array")
        self.assertIsNotNone(array_elem)
        
        children = list(array_elem)
        self.assertEqual(len(children), 2)
        self.assertEqual(children[0].tag, "number")
        self.assertEqual(children[1].tag, "string")
    
    def test_generate_declaration_ignored(self):
        """Объявления игнорируются в XML"""
        data = [{"type": "decl", "name": "x", "value": {"type": "number", "value": 10, "original": "0x0A"}}]
        xml_root = XMLGenerator.generate(data)
        
        # не должно быть элементов с типом "decl"
        for elem in xml_root.iter():
            self.assertNotEqual(elem.tag, "decl")
    
    def test_pretty_xml_formatting(self):
        """Форматирование XML с отступами"""
        data = [{"type": "number", "value": 10, "original": "0x0A"}]
        xml_root = XMLGenerator.generate(data)
        formatted = pretty_xml(xml_root)
        
        self.assertIn("<?xml", formatted)
        self.assertIn("<configuration>", formatted)
        self.assertIn("<number", formatted)
        self.assertIn("10", formatted)


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""
    
    def test_command_line_usage(self):
        """Тестирование использования через командную строки"""
        import subprocess

        test_input = '0x1A'
        expected_output = '<?xml'

        result = subprocess.run(
            ['python', '-m', 'src.config_parser'],
            input=test_input,
            capture_output=True,
            text=True
        )
    
    def test_complete_workflow(self):
        """Полный рабочий процесс"""
        config_text = """
        def port := 0x50;
        def host := "localhost";
        list($[port], $[host])
        """
        
        parser = ConfigParser()
        result = parser.parse(config_text)
        
        xml_generator = XMLGenerator()
        xml_root = xml_generator.generate(result)
        
        # Проверка структуры XML
        array_elem = xml_root.find("array")
        self.assertIsNotNone(array_elem)
        
        children = list(array_elem)
        self.assertEqual(len(children), 2)
        self.assertEqual(children[0].tag, "number")
        self.assertEqual(children[1].tag, "string")
    
    def test_file_processing(self):
        """Обработка конфигурации из файла"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write('list(0x01, 0x02, 0x03)')
            f.flush()
            
            with open(f.name, 'r') as input_file:
                input_text = input_file.read()
            
            parser = ConfigParser()
            result = parser.parse(input_text)
            self.assertEqual(len(result), 1)
        
        os.unlink(f.name)


if __name__ == '__main__':
    unittest.main()
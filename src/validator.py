import re

"""
Валидация конфигурационных файлов
"""

class ConfigValidator:
    """Валидатор конфигурационных файлов"""
    
    HEX_PATTERN = re.compile(r'^0[xX][0-9a-fA-F]+$')
    NAME_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
    
    @staticmethod
    def validate_syntax(text):
        """Базовая проверка синтаксиса"""
        if not text.strip():
            return False, "Пустой конфигурационный файл"
        
        # проверка баланса скобок
        if text.count('(') != text.count(')'):
            return False, "Несбалансированные скобки"
        
        if text.count('"') % 2 != 0:
            return False, "Несбалансированные кавычки"
        
        return True, "OK"
    
    @staticmethod
    def extract_constants(text):
        """Извлечение объявленных констант"""
        constants = {}
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('def '):
                # упрощённое извлечение имени константы
                parts = line.split()
                if len(parts) >= 4 and parts[2] == ':=':
                    const_name = parts[1]
                    if ConfigValidator.NAME_PATTERN.match(const_name):
                        constants[const_name] = i + 1  # номер строки
        
        return constants


class XMLValidator:
    """валидатор сгенерированного XML"""
    
    @staticmethod
    def validate_structure(xml_root):
        """проверка структуры XML"""
        if xml_root.tag != "configuration":
            return False, "Корневой элемент должен быть 'configuration'"
        
        return True, "OK"
    
    @staticmethod
    def is_well_formed(xml_string):
        """проверка, что XML корректно сформирован"""
        try:
            import xml.etree.ElementTree as ET
            ET.fromstring(xml_string)
            return True, "OK"
        except ET.ParseError as e:
            return False, f"Некорректный XML: {e}"
import sys
from lark import Lark, Transformer
from lark.exceptions import LarkError, UnexpectedCharacters, UnexpectedToken
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom

"""
Конфигурационный транслятор
Преобразует текст на учебном конфигурационном языке в XML
"""

# Грамматика учебного конфигурационного языка
GRAMMAR = r"""
    start: item*

    item: decl 
        | array 
        | standalone_value
        | subst              

    standalone_value: number | string
    
    decl: "def" NAME ":=" value ";"
    
    array: "list(" [value ("," value)*] ")"
    
    value: number | string | array | subst

    subst: "$[" NAME "]"

    number: HEX_NUMBER
    string: STRING
    NAME: /[a-zA-Z_][a-zA-Z0-9_]*/

    HEX_NUMBER: /0[xX][0-9a-fA-F]+/
    STRING: /"[^"]*"/

    COMMENT: /-  [^\n]*/
    %ignore COMMENT
    %ignore /[ \t\r\n]+/
"""

class ConfigTransformer(Transformer):
    def __init__(self):
        self.symbols = {}
    
    def start(self, items):
        return list(items)
    
    def item(self, items):
        return items[0]
    
    def standalone_value(self, items):
        return items[0]
    
    def decl(self, items):
        name = items[0]  # строка из NAME
        value = items[1]  # словарь с type/value
        self.symbols[name] = value
        return {"type": "decl", "name": name, "value": value}
    
    def array(self, items):
        return {"type": "array", "values": list(items)}
    
    def subst(self, items):
        name = items[0]  # строка из NAME
        if name not in self.symbols:
            raise ValueError(f"Неизвестная константа: '{name}'")
        return self.symbols[name]  # возвращаем значение константы (словарь)
    
    def value(self, items):
        return items[0]
    
    def number(self, items):
        hex_str = items[0].value
        try:
            value = int(hex_str, 16)
            return {"type": "number", "value": value, "original": hex_str}
        except ValueError:
            raise ValueError(f"Некорректное шестнадцатеричное число: '{hex_str}'")
    
    def string(self, items):
        s = items[0].value
        return {"type": "string", "value": s[1:-1]}
    
    def NAME(self, token):
        return token.value


class ConfigParser:
    """Основной класс парсера"""
    
    def __init__(self):
        self.parser = Lark(GRAMMAR, parser="lalr", transformer=ConfigTransformer())
    
    def parse(self, text):
        """Парсинг входного текста"""
        try:
            return self.parser.parse(text)
        except (LarkError, ValueError) as e:
            # Форматируем сообщение и оборачиваем в ValueError
            error_message = self._format_error(e, text)
            raise ValueError(error_message) from e  
    
    def _format_error(self, error, text):
        """Форматирование сообщения об ошибке"""
        lines = text.split('\n')
        
        if isinstance(error, UnexpectedCharacters):
            return self._format_lexical_error(error, lines)
        elif isinstance(error, UnexpectedToken):
            return self._format_syntax_error(error, lines)
        elif isinstance(error, ValueError):
            return str(error)
        else:
            return f"Ошибка парсинга: {error}"
    
    def _format_lexical_error(self, error, lines):
        """Форматирование лексической ошибки"""
        line = error.line
        column = error.column
        char = error.char
        
        error_line = lines[line - 1] if 0 < line <= len(lines) else ""
        pointer = " " * (column - 1) + "^"
        
        return (
            f"Лексическая ошибка в строке {line}, столбец {column}:\n"
            f"  {error_line}\n"
            f"  {pointer}\n"
            f"Неожиданный символ: '{char}'"
        )
    
    def _format_syntax_error(self, error, lines):
        """Форматирование синтаксической ошибки"""
        line = error.line
        column = error.column
        
        error_line = lines[line - 1] if 0 < line <= len(lines) else ""
        pointer = " " * (column - 1) + "^"
        
        expected = ", ".join(str(e) for e in error.expected) if error.expected else "другая конструкция"
        
        return (
            f"Синтаксическая ошибка в строке {line}, столбец {column}:\n"
            f"  {error_line}\n"
            f"  {pointer}\n"
            f"Ожидалось: {expected}"
        )


class XMLGenerator:
    """Генератор XML из структурированных данных"""
    
    @staticmethod
    def generate(data, root_name="configuration"):
        """Генерация XML-документа"""
        root = Element(root_name)
        
        if isinstance(data, list):
            for item in data:
                XMLGenerator._add_element(item, root)
        
        return root
    
    @staticmethod
    def _add_element(data, parent):
        """Добавление элемента в XML"""
        if isinstance(data, dict):
            elem_type = data.get("type")
            
            if elem_type == "array":
                array_elem = SubElement(parent, "array")
                for value in data.get("values", []):
                    XMLGenerator._add_element(value, array_elem)
            
            elif elem_type == "number":
                num_elem = SubElement(parent, "number")
                num_elem.set("hex", data.get("original", ""))
                num_elem.text = str(data["value"])
            
            elif elem_type == "string":
                str_elem = SubElement(parent, "string")
                str_elem.text = data["value"]
            
            elif elem_type == "decl":
                # Объявления не выводятся в итоговый XML
                pass
        
        elif isinstance(data, (int, str, float)):
            # Простые типы
            elem = SubElement(parent, "value")
            elem.text = str(data)
        
        elif isinstance(data, list):
            for item in data:
                XMLGenerator._add_element(item, parent)


def pretty_xml(element):
    """Форматирование XML с отступами"""
    xml_str = tostring(element, encoding='unicode', method='xml')
    dom = xml.dom.minidom.parseString(xml_str)
    return dom.toprettyxml(indent="  ")


def main():
    """Точка входа - обработка stdin и вывод в stdout"""
    
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Использование: python config_parser.py < input.conf > output.xml")
        print("Или: cat input.conf | python config_parser.py")
        sys.exit(0)
    
    # чтение из стандартного ввода
    input_text = sys.stdin.read()
    
    if not input_text.strip():
        print("Ошибка: входной текст пуст", file=sys.stderr)
        sys.exit(1)
    
    # парсинг и преобразование
    try:
        parser = ConfigParser()
        result = parser.parse(input_text)
        
        xml_generator = XMLGenerator()
        xml_root = xml_generator.generate(result)
        
        # вывод в стандартный вывод
        output_xml = pretty_xml(xml_root)
        sys.stdout.write(output_xml)
        
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
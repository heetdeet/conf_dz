# Конфигурационный транслятор - Вариант 16

## Описание
Инструмент командной строки для преобразования текста на учебном конфигурационном языке в XML. Реализует вариант №16 задания по дисциплине "Конфигурационное управление".

## Синтаксис языка

### Основные конструкции:
- **Числа:** `0x1A` (шестнадцатеричные)
- **Строки:** `"текст"`
- **Массивы:** `list(значение, значение, ...)`
- **Константы:** `def имя := значение;`
- **Подстановка:** `$[имя]`
- **Комментарии:** `-  текст`

### Пример:
```conf
def timeout := 0x3E8;
def server := "localhost";
list($[timeout], $[server], 0x01)
```

## Установка

### Способ 1: Установка как пакета
```bash
pip install -e .
```

### Способ 2: Прямое использование
```bash
python src/config_parser.py < input.conf > output.xml
```

## Использование

### Командная строка:
```bash
# Из файла
python src/config_parser.py < config.conf > output.xml

# Прямой ввод
echo '0x1A' | python src/config_parser.py

# Помощь
python src/config_parser.py --help
```

### Как модуль Python:
```python
from src.config_parser import ConfigParser, XMLGenerator

parser = ConfigParser()
result = parser.parse('list(0x01, 0x02)')
xml = XMLGenerator.generate(result)
```

## Тестирование

```bash
# Запуск всех тестов
python -m pytest tests/

# Запуск конкретного теста
python -m pytest tests/test_parser.py -v

# Запуск с покрытием
python -m pytest --cov=src tests/
```

## Примеры

Примеры конфигураций находятся в папке `examples/`:

```bash
# Преобразование примеров
python src/config_parser.py < examples/network.conf > network.xml
python src/config_parser.py < examples/game.conf > game.xml
```

## Структура проекта

```
.
├── src/                    # Исходный код
│   ├── config_parser.py   # Основной парсер
│   ├── validator.py       # Валидация
│   └── xml_generator.py   # Генерация XML
├── tests/                 # Тесты
├── examples/             # Примеры конфигураций
├── requirements.txt      # Зависимости
└── README.md            # Этот файл
```

## Требования

- Python 3.8 или выше
- Зависимости: `lark-parser`


## **Использование:**

1. **Клонировать репозиторий:**
   ```bash
   git clone https://github.com/heetdeet/conf_dz.git
   cd conf_dz.git
   ```

2. **Установить зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Запустить тесты:**
   ```bash
   python -m pytest tests/
   ```

4. **Протестировать на примерах:**
   ```bash
   python src/config_parser.py < examples/network.conf
   python src/config_parser.py < config.conf > output.xml
   ```

5. **Использовать как утилиту:**
   ```bash
   echo list(0x01, 0x02, 0x03) | python src/config_parser.py
   ```

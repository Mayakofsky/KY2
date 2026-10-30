"""Тесты для модуля конфигурации."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config_parser import ConfigParser

EXPECTED_MAX_DEPTH = 3


def test_load_config_defaults():
    print("\n--- Тест 1: загрузка штатного config.ini ---")
    path = os.path.join(
        os.path.dirname(__file__), '..', 'src', 'config.ini'
    )
    print("Ввод (путь):", path)
    parser = ConfigParser(path)
    parser.load_config()
    print("Вывод (config_data):", parser.config_data)
    assert parser.config_data['package_name'] == 'busybox'
    assert parser.config_data['test_mode'] is False
    assert parser.config_data['max_depth'] == EXPECTED_MAX_DEPTH


def test_missing_file():
    print("\n--- Тест 2: отсутствующий файл ---")
    path = 'nonexistent.ini'
    print("Ввод (путь):", path)
    parser = ConfigParser(path)
    try:
        parser.load_config()
        print("Вывод: исключение НЕ выброшено")
        assert False
    except FileNotFoundError as e:
        print("Вывод (FileNotFoundError):", e)


def test_missing_section():
    print("\n--- Тест 3: отсутствующая секция [Settings] ---")
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.ini', delete=False, encoding='utf-8'
    ) as f:
        f.write('[Other]\nkey=value\n')
        path = f.name
    print("Ввод (содержимое файла): [Other]\\nkey=value")
    parser = ConfigParser(path)
    try:
        parser.load_config()
        print("Вывод: исключение НЕ выброшено")
        assert False
    except ValueError as e:
        print("Вывод (ValueError):", e)
    os.unlink(path)


def test_missing_param():
    print("\n--- Тест 4: отсутствующий обязательный параметр ---")
    content = (
        '[Settings]\n'
        'package_name = test\n'
        'repo_url = http://example.com\n'
    )
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.ini', delete=False, encoding='utf-8'
    ) as f:
        f.write(content)
        path = f.name
    print("Ввод (содержимое файла):", repr(content))
    parser = ConfigParser(path)
    try:
        parser.load_config()
        print("Вывод: исключение НЕ выброшено")
        assert False
    except ValueError as e:
        print("Вывод (ValueError):", e)
    os.unlink(path)


def test_invalid_type():
    print("\n--- Тест 5: неверный тип данных (max_depth) ---")
    content = (
        '[Settings]\n'
        'package_name = test\n'
        'repo_url = http://example.com\n'
        'test_mode = False\n'
        'package_version = 1.0\n'
        'max_depth = abc\n'
    )
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.ini', delete=False, encoding='utf-8'
    ) as f:
        f.write(content)
        path = f.name
    print("Ввод (содержимое файла):", repr(content))
    parser = ConfigParser(path)
    try:
        parser.load_config()
        print("Вывод: исключение НЕ выброшено")
        assert False
    except ValueError as e:
        print("Вывод (ValueError):", e)
    os.unlink(path)


def test_display_config():
    print("\n--- Тест 6: вывод display_config ---")
    path = os.path.join(os.path.dirname(__file__), '..', 'src', 'config.ini')
    parser = ConfigParser(path)
    parser.load_config()
    parser.display_config()
    print("(проверка вывода выше)")

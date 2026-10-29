"""Тесты для модуля конфигурации."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config_parser import ConfigParser  # noqa: E402


def test_load_config_defaults():
    """Проверка загрузки конфигурации из config.ini."""
    parser = ConfigParser(os.path.join(
        os.path.dirname(__file__), '..', 'src', 'config.ini'
    ))
    parser.load_config()
    assert parser.config_data['package_name'] == 'busybox'
    assert parser.config_data['repo_url'] == 'https://dl-cdn.alpinelinux.org/alpine/edge/main'
    assert parser.config_data['test_mode'] is False
    assert parser.config_data['package_version'] == '1.36.1-r15'
    assert parser.config_data['max_depth'] == 3


def test_missing_file():
    """Проверка ошибки при отсутствии файла конфигурации."""
    parser = ConfigParser('nonexistent.ini')
    try:
        parser.load_config()
        assert False, "Ожидалось исключение FileNotFoundError"
    except FileNotFoundError:
        pass


def test_missing_section():
    """Проверка ошибки при отсутствии секции [Settings]."""
    import configparser
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.ini', delete=False, encoding='utf-8'
    ) as f:
        f.write('[Other]\nkey=value\n')
        tmp_path = f.name

    try:
        parser = ConfigParser(tmp_path)
        try:
            parser.load_config()
            assert False, "Ожидалось исключение ValueError"
        except ValueError as e:
            assert 'Settings' in str(e)
    finally:
        os.unlink(tmp_path)

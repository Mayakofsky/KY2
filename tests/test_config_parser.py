"""Тесты для модуля конфигурации."""
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config_parser import ConfigParser  # noqa: E402


@pytest.fixture
def valid_config_path():
    """Возвращает путь к валидному конфигурационному файлу."""
    return os.path.join(os.path.dirname(__file__), '..', 'src', 'config.ini')


@pytest.fixture
def temp_ini():
    """Фабрика временных INI-файлов с автоматической очисткой."""
    created = []

    def _make(content: str) -> str:
        f = tempfile.NamedTemporaryFile(
            mode='w', suffix='.ini', delete=False, encoding='utf-8'
        )
        f.write(content)
        f.close()
        created.append(f.name)
        return f.name

    yield _make

    for path in created:
        if os.path.exists(path):
            os.unlink(path)


class TestLoadConfigSuccess:
    """Тесты успешной загрузки конфигурации."""

    def test_load_default_config_values(self, valid_config_path):
        """Проверка загрузки конфигурации из штатного config.ini."""
        parser = ConfigParser(valid_config_path)
        parser.load_config()

        assert parser.config_data['package_name'] == 'busybox'
        assert parser.config_data['repo_url'] == (
            'https://dl-cdn.alpinelinux.org/alpine/edge/main'
        )
        assert parser.config_data['test_mode'] is False
        assert parser.config_data['package_version'] == '1.36.1-r15'
        assert parser.config_data['max_depth'] == 3

    def test_all_five_params_present(self, valid_config_path):
        """Проверка наличия всех пяти обязательных параметров."""
        parser = ConfigParser(valid_config_path)
        parser.load_config()

        expected_keys = {
            'package_name', 'repo_url', 'test_mode',
            'package_version', 'max_depth'
        }
        assert set(parser.config_data.keys()) == expected_keys

    def test_test_mode_true(self, temp_ini):
        """Проверка корректного парсинга test_mode = True."""
        path = temp_ini(
            '[Settings]\n'
            'package_name = curl\n'
            'repo_url = /tmp/repo\n'
            'test_mode = True\n'
            'package_version = 8.0.0\n'
            'max_depth = 5\n'
        )
        parser = ConfigParser(path)
        parser.load_config()
        assert parser.config_data['test_mode'] is True

    def test_max_depth_zero(self, temp_ini):
        """Проверка граничного значения max_depth = 0."""
        path = temp_ini(
            '[Settings]\n'
            'package_name = wget\n'
            'repo_url = http://example.com\n'
            'test_mode = False\n'
            'package_version = 1.0\n'
            'max_depth = 0\n'
        )
        parser = ConfigParser(path)
        parser.load_config()
        assert parser.config_data['max_depth'] == 0

    def test_max_depth_large_value(self, temp_ini):
        """Проверка большого значения max_depth."""
        path = temp_ini(
            '[Settings]\n'
            'package_name = bash\n'
            'repo_url = http://example.com\n'
            'test_mode = False\n'
            'package_version = 5.2\n'
            'max_depth = 999\n'
        )
        parser = ConfigParser(path)
        parser.load_config()
        assert parser.config_data['max_depth'] == 999

    def test_empty_string_values_allowed(self, temp_ini):
        """Проверка что пустые строковые значения допустимы."""
        path = temp_ini(
            '[Settings]\n'
            'package_name = \n'
            'repo_url = \n'
            'test_mode = False\n'
            'package_version = \n'
            'max_depth = 1\n'
        )
        parser = ConfigParser(path)
        parser.load_config()
        assert parser.config_data['package_name'] == ''
        assert parser.config_data['repo_url'] == ''
        assert parser.config_data['package_version'] == ''

    def test_config_data_empty_before_load(self, valid_config_path):
        """Проверка что config_data пуст до вызова load_config."""
        parser = ConfigParser(valid_config_path)
        assert parser.config_data == {}


class TestMissingFile:
    """Тесты обработки отсутствующего файла конфигурации."""

    def test_missing_file_raises_file_not_found(self):
        """Проверка FileNotFoundError при отсутствии файла."""
        parser = ConfigParser('nonexistent_config_abc123.ini')
        with pytest.raises(FileNotFoundError) as exc_info:
            parser.load_config()
        assert 'nonexistent_config_abc123.ini' in str(exc_info.value)

    def test_missing_file_message_contains_path(self):
        """Проверка что сообщение об ошибке содержит путь к файлу."""
        path = '/some/weird/path/config.ini'
        parser = ConfigParser(path)
        with pytest.raises(FileNotFoundError) as exc_info:
            parser.load_config()
        assert path in str(exc_info.value)


class TestMissingSection:
    """Тесты обработки отсутствующей секции [Settings]."""

    def test_missing_settings_section(self, temp_ini):
        """Проверка ValueError при отсутствии секции [Settings]."""
        path = temp_ini('[Other]\nkey=value\n')
        parser = ConfigParser(path)
        with pytest.raises(ValueError) as exc_info:
            parser.load_config()
        assert 'Settings' in str(exc_info.value)

    def test_empty_file_raises_value_error(self, temp_ini):
        """Проверка ValueError для пустого файла."""
        path = temp_ini('')
        parser = ConfigParser(path)
        with pytest.raises(ValueError) as exc_info:
            parser.load_config()
        assert 'Settings' in str(exc_info.value)

    def test_wrong_section_name(self, temp_ini):
        """Проверка ValueError при другом имени секции."""
        path = temp_ini('[settings]\npackage_name = test\n')
        parser = ConfigParser(path)
        with pytest.raises(ValueError) as exc_info:
            parser.load_config()
        assert 'Settings' in str(exc_info.value)


class TestMissingParams:
    """Тесты обработки отсутствующих обязательных параметров."""

    @pytest.mark.parametrize('missing_param', [
        'package_name', 'repo_url', 'test_mode',
        'package_version', 'max_depth'
    ])
    def test_missing_required_param(self, temp_ini, missing_param):
        """Проверка ValueError при отсутствии каждого обязательного параметра."""
        all_params = {
            'package_name': 'test',
            'repo_url': 'http://example.com',
            'test_mode': 'False',
            'package_version': '1.0',
            'max_depth': '3',
        }
        del all_params[missing_param]

        content = '[Settings]\n'
        for k, v in all_params.items():
            content += f'{k} = {v}\n'

        path = temp_ini(content)
        parser = ConfigParser(path)
        with pytest.raises(ValueError) as exc_info:
            parser.load_config()
        assert missing_param in str(exc_info.value)


class TestInvalidTypes:
    """Тесты обработки неверных типов данных."""

    def test_invalid_max_depth_non_integer(self, temp_ini):
        """Проверка ValueError при нецелом max_depth."""
        path = temp_ini(
            '[Settings]\n'
            'package_name = test\n'
            'repo_url = http://example.com\n'
            'test_mode = False\n'
            'package_version = 1.0\n'
            'max_depth = abc\n'
        )
        parser = ConfigParser(path)
        with pytest.raises(ValueError) as exc_info:
            parser.load_config()
        assert 'max_depth' in str(exc_info.value).lower() or 'тип' in str(exc_info.value).lower()

    def test_invalid_max_depth_float(self, temp_ini):
        """Проверка ValueError при дробном max_depth."""
        path = temp_ini(
            '[Settings]\n'
            'package_name = test\n'
            'repo_url = http://example.com\n'
            'test_mode = False\n'
            'package_version = 1.0\n'
            'max_depth = 3.5\n'
        )
        parser = ConfigParser(path)
        with pytest.raises(ValueError):
            parser.load_config()

    def test_invalid_test_mode(self, temp_ini):
        """Проверка ValueError при неверном значении test_mode."""
        path = temp_ini(
            '[Settings]\n'
            'package_name = test\n'
            'repo_url = http://example.com\n'
            'test_mode = maybe\n'
            'package_version = 1.0\n'
            'max_depth = 3\n'
        )
        parser = ConfigParser(path)
        with pytest.raises(ValueError) as exc_info:
            parser.load_config()
        assert 'test_mode' in str(exc_info.value).lower() or 'тип' in str(exc_info.value).lower()

    def test_invalid_test_mode_numeric(self, temp_ini):
        """Проверка ValueError при числовом значении test_mode."""
        path = temp_ini(
            '[Settings]\n'
            'package_name = test\n'
            'repo_url = http://example.com\n'
            'test_mode = 2\n'
            'package_version = 1.0\n'
            'max_depth = 3\n'
        )
        parser = ConfigParser(path)
        with pytest.raises(ValueError):
            parser.load_config()


class TestDisplayConfig:
    """Тесты вывода конфигурации."""

    def test_display_config_output(self, valid_config_path, capsys):
        """Проверка формата вывода display_config."""
        parser = ConfigParser(valid_config_path)
        parser.load_config()
        parser.display_config()

        captured = capsys.readouterr()
        output = captured.out

        assert 'Параметры конфигурации' in output
        assert 'package_name: busybox' in output
        assert 'repo_url: https://dl-cdn.alpinelinux.org/alpine/edge/main' in output
        assert 'test_mode: False' in output
        assert 'package_version: 1.36.1-r15' in output
        assert 'max_depth: 3' in output

    def test_display_config_all_keys_present(self, valid_config_path, capsys):
        """Проверка что все ключи присутствуют в выводе."""
        parser = ConfigParser(valid_config_path)
        parser.load_config()
        parser.display_config()

        captured = capsys.readouterr()
        for key in ['package_name', 'repo_url', 'test_mode',
                     'package_version', 'max_depth']:
            assert key in captured.out

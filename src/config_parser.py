import configparser
import os


class ConfigParser:
    """Класс для загрузки, валидации и отображения конфигурации."""

    def __init__(self, file_path: str):
        """Инициализация парсера конфигурации.

        Args:
            file_path: Путь к INI-файлу конфигурации.
        """
        self.file_path = file_path
        self.config_data = {}

    def load_config(self):
        """Загрузка и валидация конфигурационного файла.

        Raises:
            FileNotFoundError: Если файл конфигурации не найден.
            ValueError: Если отсутствует секция [Settings],
                обязательный параметр или неверный тип данных.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(
                f"Файл {self.file_path} не найден."
            )

        parser = configparser.ConfigParser()
        parser.read(self.file_path, encoding='utf-8')

        if 'Settings' not in parser:
            raise ValueError(
                "Секция [Settings] отсутствует в файле."
            )

        settings = parser['Settings']

        try:
            self.config_data = {
                'package_name': settings['package_name'],
                'repo_url': settings['repo_url'],
                'test_mode': settings.getboolean('test_mode'),
                'package_version': settings['package_version'],
                'max_depth': settings.getint('max_depth')
            }
        except KeyError as missing_key:
            raise ValueError(
                f"Отсутствует обязательный параметр: {missing_key}"
            )
        except ValueError:
            raise ValueError(
                "Неверный тип данных: max_depth должно быть "
                "целым числом, test_mode — True/False."
            )

    def display_config(self):
        """Вывод всех параметров конфигурации в формате ключ-значение."""
        print("Параметры конфигурации")
        for key, value in self.config_data.items():
            print(f"{key}: {value}")
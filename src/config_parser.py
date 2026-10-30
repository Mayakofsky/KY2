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

    def _validate_file_and_section(self):
        """Проверка существования файла и наличия секции [Settings].

        Returns:
            configparser.SectionProxy: секция Settings.

        Raises:
            FileNotFoundError: Если файл не найден.
            ValueError: Если секция [Settings] отсутствует.
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

        return parser['Settings']

    def _parse_settings(self, settings):
        """Парсинг и валидация параметров из секции Settings.

        Args:
            settings: Секция Settings из ConfigParser.

        Raises:
            ValueError: Если параметр отсутствует или тип неверен.
        """
        required = (
            'package_name', 'repo_url', 'test_mode',
            'package_version', 'max_depth'
        )
        settings_dict = dict(settings)
        missing = [k for k in required if k not in settings_dict]
        if missing:
            raise ValueError(
                f"Отсутствует обязательный параметр: {missing[0]}"
            )

        try:
            self.config_data = {
                'package_name': settings['package_name'],
                'repo_url': settings['repo_url'],
                'test_mode': settings.getboolean('test_mode'),
                'package_version': settings['package_version'],
                'max_depth': settings.getint('max_depth')
            }
        except ValueError:
            raise ValueError(
                "Неверный тип данных: max_depth должно быть "
                "целым числом, test_mode — True/False."
            )

    def load_config(self):
        """Загрузка и валидация конфигурационного файла.

        Raises:
            FileNotFoundError: Если файл конфигурации не найден.
            ValueError: Если отсутствует секция [Settings],
                обязательный параметр или неверный тип данных.
        """
        settings = self._validate_file_and_section()
        self._parse_settings(settings)

    def display_config(self):
        """Вывод всех параметров конфигурации в формате ключ-значение."""
        print("Параметры конфигурации")
        for key, value in self.config_data.items():
            print(f"{key}: {value}")
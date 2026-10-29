import sys
from config_parser import ConfigParser

CONFIG_PATH = 'src/config.ini'

def main():
    """Точка входа приложения.

    Загружает конфигурацию и выводит параметры на экран.
    При ошибке выводит сообщение в stderr и завершает работу с кодом 1.
    """
    manager = ConfigParser(CONFIG_PATH)

    try:
        manager.load_config()
        manager.display_config()
    except Exception as error:
        print(f"Ошибка конфигурации: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
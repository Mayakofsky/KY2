import sys
from config_parser import ConfigParser
from dependency_collector import DependencyCollector

CONFIG_PATH = 'src/config.ini'


def main():
    """Точка входа приложения.

    Загружает конфигурацию и выводит прямые зависимости пакета.
    """
    config = ConfigParser(CONFIG_PATH)

    try:
        config.load_config()
        collector = DependencyCollector(config.config_data['repo_url'])
        deps = collector.get_direct_dependencies(
            config.config_data['package_name'],
            config.config_data['package_version']
        )

        pkg_name = config.config_data['package_name']
        pkg_ver = config.config_data['package_version']
        print(f"Прямые зависимости пакета {pkg_name} ({pkg_ver}):")
        if not deps:
            print("  (зависимостей нет)")
        for dep in deps:
            print(f"- {dep}")
    except Exception as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

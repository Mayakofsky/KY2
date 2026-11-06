import io
import tarfile
import urllib.request

HTTP_TIMEOUT_SECONDS = 10


class DependencyCollector:
    """Класс для сбора прямых зависимостей пакета Alpine Linux."""

    def __init__(self, repo_url: str):
        """Инициализация коллектора зависимостей.

        Args:
            repo_url: URL-адрес репозитория Alpine Linux.
        """
        self.repo_url = repo_url.rstrip('/')

    def _fetch_index_content(self) -> str:
        """Загрузка и распаковка файла APKINDEX из репозитория.

        Returns:
            str: Содержимое текстового файла APKINDEX.
        """
        index_url = f"{self.repo_url}/APKINDEX.tar.gz"
        request = urllib.request.Request(
            index_url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(
            request, timeout=HTTP_TIMEOUT_SECONDS
        ) as response:
            archive_data = response.read()

        with tarfile.open(fileobj=io.BytesIO(archive_data), mode='r:gz') as tar:
            index_file = tar.extractfile('APKINDEX')
            if index_file is None:
                raise ValueError("APKINDEX не найден в репозитории.")
            return index_file.read().decode('utf-8', errors='ignore')

    def get_direct_dependencies(
        self, pkg_name: str, pkg_ver: str
    ) -> list[str]:
        """Получение прямых зависимостей пакета указанной версии.

        Args:
            pkg_name: Имя анализируемого пакета.
            pkg_ver: Версия пакета.

        Returns:
            list[str]: Список имен зависимостей.

        Raises:
            ValueError: Если пакет с указанной версией не найден.
        """
        raw_content = self._fetch_index_content()
        blocks = raw_content.split('\n\n')

        for block in blocks:
            fields = {}
            for line in block.strip().split('\n'):
                if ':' in line:
                    key, _, val = line.partition(':')
                    fields[key] = val.strip()

            if fields.get('P') == pkg_name and fields.get('V') == pkg_ver:
                raw_deps = fields.get('D', '')
                if not raw_deps:
                    return []
                return raw_deps.split()

        raise ValueError(
            f"Пакет '{pkg_name}' версии '{pkg_ver}' не найден."
        )

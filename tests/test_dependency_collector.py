"""Тесты для модуля сбора зависимостей Alpine Linux."""
import io
import os
import sys
import tarfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dependency_collector import DependencyCollector

EXPECTED_CURL_DEPS_COUNT = 3

SAMPLE_INDEX = (
    "P:busybox\n"
    "V:1.36.1-r31\n"
    "D:so:libc.musl-x86_64.so.1\n\n"
    "P:curl\n"
    "V:8.14.1-r2\n"
    "D:libcurl=8.14.1-r2 so:libc.musl-x86_64.so.1 so:libz.so.1\n\n"
    "P:empty-pkg\n"
    "V:1.0.0-r0\n\n"
)


def _build_fake_tar_gz(content: str) -> bytes:
    """Создание байтов архива tar.gz с файлом APKINDEX внутри."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz') as tar:
        encoded = content.encode('utf-8')
        info = tarfile.TarInfo(name='APKINDEX')
        info.size = len(encoded)
        tar.addfile(info, io.BytesIO(encoded))
    return buf.getvalue()


class FakeResponse:
    """Мок-класс для ответа urllib.request.urlopen."""

    def __init__(self, data: bytes):
        self.data = data

    def read(self) -> bytes:
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def test_get_direct_dependencies_success(monkeypatch):
    """Тест успешного получения прямых зависимостей существующего пакета."""
    print("\n--- Тест 7: получение прямых зависимостей (busybox) ---")
    fake_data = _build_fake_tar_gz(SAMPLE_INDEX)
    monkeypatch.setattr(
        'urllib.request.urlopen',
        lambda req, timeout=10: FakeResponse(fake_data)
    )

    collector = DependencyCollector("https://example.com/alpine/main/x86_64")
    print("Ввод: пакет='busybox', версия='1.36.1-r31'")
    deps = collector.get_direct_dependencies("busybox", "1.36.1-r31")
    print("Вывод (найденные прямые зависимости):", deps)
    assert deps == ["so:libc.musl-x86_64.so.1"]


def test_get_multiple_dependencies(monkeypatch):
    """Тест получения нескольких прямых зависимостей пакета."""
    print("\n--- Тест 8: пакет с несколькими зависимостями (curl) ---")
    fake_data = _build_fake_tar_gz(SAMPLE_INDEX)
    monkeypatch.setattr(
        'urllib.request.urlopen',
        lambda req, timeout=10: FakeResponse(fake_data)
    )

    collector = DependencyCollector("https://example.com/alpine/main/x86_64")
    print("Ввод: пакет='curl', версия='8.14.1-r2'")
    deps = collector.get_direct_dependencies("curl", "8.14.1-r2")
    print("Вывод (найденные прямые зависимости):", deps)
    assert len(deps) == EXPECTED_CURL_DEPS_COUNT
    assert "libcurl=8.14.1-r2" in deps
    assert "so:libz.so.1" in deps


def test_package_without_dependencies(monkeypatch):
    """Тест для пакета, у которого вообще нет зависимостей (поле D пустое)."""
    print("\n--- Тест 9: пакет без зависимостей (empty-pkg) ---")
    fake_data = _build_fake_tar_gz(SAMPLE_INDEX)
    monkeypatch.setattr(
        'urllib.request.urlopen',
        lambda req, timeout=10: FakeResponse(fake_data)
    )

    collector = DependencyCollector("https://example.com/alpine/main/x86_64")
    print("Ввод: пакет='empty-pkg', версия='1.0.0-r0'")
    deps = collector.get_direct_dependencies("empty-pkg", "1.0.0-r0")
    print("Вывод (найденные прямые зависимости):", deps)
    assert deps == []


def test_package_not_found_raises_error(monkeypatch):
    """Тест генерации ошибки, если имя пакета не найдено в репозитории."""
    print("\n--- Тест 10: несуществующий пакет ---")
    fake_data = _build_fake_tar_gz(SAMPLE_INDEX)
    monkeypatch.setattr(
        'urllib.request.urlopen',
        lambda req, timeout=10: FakeResponse(fake_data)
    )

    collector = DependencyCollector("https://example.com/alpine/main/x86_64")
    print("Ввод: пакет='unknown-pkg', версия='1.0.0'")
    with pytest.raises(ValueError, match="не найден") as exc_info:
        collector.get_direct_dependencies("unknown-pkg", "1.0.0")
    print("Вывод (перехваченная ошибка):", exc_info.value)


def test_wrong_version_raises_error(monkeypatch):
    """Тест генерации ошибки, если имя пакета есть, но версия отличается."""
    print("\n--- Тест 11: несовпадающая версия пакета ---")
    fake_data = _build_fake_tar_gz(SAMPLE_INDEX)
    monkeypatch.setattr(
        'urllib.request.urlopen',
        lambda req, timeout=10: FakeResponse(fake_data)
    )

    collector = DependencyCollector("https://example.com/alpine/main/x86_64")
    print("Ввод: пакет='busybox', неверная версия='9.9.9-r0'")
    with pytest.raises(ValueError, match="не найден") as exc_info:
        collector.get_direct_dependencies("busybox", "9.9.9-r0")
    print("Вывод (перехваченная ошибка):", exc_info.value)

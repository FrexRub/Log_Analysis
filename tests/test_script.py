import sys
import pytest
from unittest.mock import patch, mock_open

from main import main, check_files, EndpointClass, read_log_file


def test_without_args():
    test_args = ["main.py"]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as exc:
            main()
        assert "Необходимо задать входные параметры" in str(exc.value)


def test_invalid_log_files():
    test_args = ["main.py", "app.log1"]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as exc:
            main()
        assert "Не указаны лог файлы с расширением *.log" in str(exc.value)


def test_invalid_report_name():
    test_args = ["main.py", "app.log", "--report", "handlers!"]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as exc:
            main()
        assert "Имя отчета должно содержать только буквы и цифры" in str(exc.value)


def test_invalid_params():
    test_args = ["main.py", "app.log", "--report"]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as exc:
            main()
        assert (
            "Аргумент --report указывается в конце команды с указанием имени отчета"
            in str(exc.value)
        )


def test_invalid_check_files():
    test_args = ["main.py", "test.log"]
    with patch.object(sys, "argv", test_args):
        with patch("main.check_files", return_value=False):
            with pytest.raises(SystemExit) as exc:
                main()
            assert "Файл с логами не найден" in str(exc.value)


def test_check_files_true(name_file):
    assert check_files([name_file]) is True


def test_check_files_false():
    assert check_files(["test.log"]) is False


def test_endpoint_class_init():
    endpoint = EndpointClass()
    assert endpoint.count_level == {
        "debug": 0,
        "info": 0,
        "warning": 0,
        "error": 0,
        "critical": 0,
    }


def test_read_log_file():
    log_content = """
    2025-03-28 12:44:46,000 INFO django.request: GET /api/v1/reviews/ 204 OK [192.168.1.59]
    2025-03-28 12:21:51,000 INFO django.request: GET /admin/dashboard/ 200 OK [192.168.1.68]
    2025-03-28 12:40:47,000 CRITICAL django.core.management: DatabaseError: Deadlock detected
    2025-03-28 12:25:45,000 DEBUG django.db.backends: (0.41) SELECT * FROM 'products' WHERE id = 4;
    2025-03-28 12:03:09,000 DEBUG django.db.backends: (0.19) SELECT * FROM 'users' WHERE id = 32;
    2025-03-28 12:05:13,000 INFO django.request: GET /api/v1/reviews/ 201 OK [192.168.1.97]
    2025-03-28 12:31:51,000 ERROR django.request: Internal Server Error: /api/v1/support/ [192.168.1.90] - SuspiciousOperati
    """

    with patch("builtins.open", mock_open(read_data=log_content)):
        result = read_log_file("test.log")

        assert result.get("/api/v1/reviews/")
        assert result.get("/admin/dashboard/")
        assert result.get("/api/v1/support/")

        assert result["/api/v1/reviews/"].count_level["info"] == 2
        assert result["/admin/dashboard/"].count_level["info"] == 1
        assert result["/api/v1/support/"].count_level["error"] == 1

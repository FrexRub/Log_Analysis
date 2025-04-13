import sys
import pytest
from unittest.mock import patch, mock_open

from main import (
    main,
    check_files,
    EndpointClass,
    read_log_file,
    write_report_to_file,
    write_report_to_console,
    gen_report,
)


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


def test_write_report_to_file(tmp_path):
    report_file = tmp_path / "report.txt"
    endpoints = {"/api/users": EndpointClass()}
    endpoints["/api/users"].count_level["info"] = 5
    all_levels = {"debug": 0, "info": 5, "warning": 0, "error": 0, "critical": 0}

    write_report_to_file(endpoints, all_levels, str(report_file))
    content = report_file.read_text()

    assert "Total requests: 5" in content
    assert "HANDLER" in content
    assert "/api/users" in content
    assert "5" in content


def test_write_report_to_console(capsys):
    endpoints = {"/api/users": EndpointClass()}
    endpoints["/api/users"].count_level["error"] = 2
    all_levels = {"debug": 0, "info": 0, "warning": 0, "error": 2, "critical": 0}

    write_report_to_console(endpoints, all_levels)

    out, err = capsys.readouterr()
    assert "Total requests: 2" in out
    assert "HANDLER" in out
    assert "/api/users" in out
    assert "2" in out


@patch("main.Pool")
def test_gen_report_with_file(mock_pool, tmp_path):
    mock_pool.return_value.__enter__.return_value.map.return_value = [
        {"/api/users": EndpointClass()}
    ]

    report_file = tmp_path / "report.txt"
    gen_report(["app.log"], str(report_file))

    assert report_file.exists()


@patch("main.Pool")
def test_gen_report_with_console_output(mock_pool, capsys):
    endpoint = EndpointClass()
    endpoint.count_level = {
        "debug": 0,
        "info": 0,
        "warning": 5,
        "error": 0,
        "critical": 0,
    }

    mock_pool.return_value.__enter__.return_value.map.return_value = [
        {"/api/users": endpoint}
    ]

    gen_report(["app.log"], None)

    out, err = capsys.readouterr()
    assert "Total requests: 5" in out

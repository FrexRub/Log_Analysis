import sys
import pytest
from unittest.mock import patch

from main import main, check_files


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


def test_check_files(name_file):
    assert check_files([name_file]) is True

import os.path
import sys
import re
from multiprocessing import Pool, cpu_count

INDEX_LEVEL_IN_LOG = 2
LEVEL_COUNT = (("debug", 0), ("info", 0), ("warning", 0), ("error", 0), ("critical", 0))

HEADER: str = (
        "HANDLER".ljust(30)
        + "DEBUG".ljust(10)
        + "INFO".ljust(10)
        + "WARNING".ljust(10)
        + "ERROR".ljust(10)
        + "CRITICAL".ljust(10)
)


class EndpointClass:
    __slots__ = ("count_level",)

    def __init__(self) -> None:
        self.count_level: dict[str, int] = dict(LEVEL_COUNT)


def read_log_file(name_file: str) -> dict[str, EndpointClass]:
    """
    Чтение и обработка лог-файла
    :param name_file: имя лог-файла
    :type name_file: str
    :rtype: dict[str, EndpointClass]
    :return: возвращает словарь с данными по уровням логирования по каждой ручке
    """
    dict_endpoint: dict[str, EndpointClass] = dict()
    with open(name_file, "r", encoding="utf-8") as file:
        for line in file:
            if "django.request" in line:
                str_log: list[str] = line.strip().split()
                level_log: str = str_log[INDEX_LEVEL_IN_LOG].lower()

                result = re.search(r"\s\/\S+", line)
                name_api: str | None = result.group(0).strip() if result else None

                if name_api is not None:
                    if dict_endpoint.get(name_api) is None:
                        dict_endpoint[name_api] = EndpointClass()
                        dict_endpoint[name_api].count_level[level_log] += 1
                    else:
                        dict_endpoint[name_api].count_level[level_log] += 1

        return dict_endpoint


def write_report_to_file(
        resul_report: dict[str, EndpointClass],
        all_level_error: dict[str, int],
        name_report: str,
) -> None:
    """
    Формирование и запись отчета в файл
    :param resul_report: словарь с данными по уровням логирования по каждой ручке
    :type resul_report: dict[str, EndpointClass]
    :param all_level_error: словарь с общими данными по уровням логирования
    :type all_level_error: dict[str, int]
    :param name_report: имя файла формируемого отчета
    :type name_report: str
    """
    total_req: int = 0
    record_down: str = " ".ljust(30)
    for _, val in all_level_error.items():
        total_req = total_req + val
        record_down = record_down + str(val).ljust(10)
    record_down = record_down + "\n"

    with open(name_report, "w") as f:
        f.write(f"Total requests: {total_req}\n\n")
        f.write(HEADER + "\n")

        for key, endpoint in resul_report.items():
            record_log: str = key.ljust(30)
            for key_l, val_l in endpoint.count_level.items():
                record_log = record_log + str(val_l).ljust(10)
            record_log = record_log + "\n"
            f.write(record_log)
        f.write(record_down)


def write_report_to_console(
        resul_report: dict[str, EndpointClass],
        all_level_error: dict[str, int],
) -> None:
    """
    Формирование и вывод отчета на консоль
    :param resul_report: словарь с данными по уровням логирования по каждой ручке
    :type resul_report: dict[str, EndpointClass]
    :param all_level_error: словарь с общими данными по уровням логирования
    :type all_level_error: dict[str, int]
    """
    total_req: int = 0
    record_down: str = " ".ljust(30)
    for _, val in all_level_error.items():
        total_req = total_req + val
        record_down = record_down + str(val).ljust(10)
    record_down = record_down

    print(f"Total requests: {total_req}", "\n")
    print(HEADER)

    for key, endpoint in resul_report.items():
        record_log: str = key.ljust(30)
        for key_l, val_l in endpoint.count_level.items():
            record_log = record_log + str(val_l).ljust(10)

        print(record_log)
    print(record_down)


def gen_report(name_files: list[str], name_report: str | None) -> None:
    """
    Подготовка данных для формирования отчетов
    :param name_files: список имен лог-файлов
    :type name_files: list[str]
    :param name_report: имя файла отчета (при необходимости)
    :type name_report: str | None
    """
    with Pool(processes=cpu_count()) as pod:
        slot_reports: list[dict[str, EndpointClass]] = pod.map(
            read_log_file, name_files
        )

    resul_report: dict[str, EndpointClass] = dict()
    all_level_error: dict[str, int] = dict(LEVEL_COUNT)

    for report in slot_reports:
        for api, api_count_level in report.items():
            if resul_report.get(api) is None:
                resul_report[api] = api_count_level
                for key_api, error_api in api_count_level.count_level.items():
                    all_level_error[key_api] += error_api
            else:
                for key, val in api_count_level.count_level.items():
                    resul_report[api].count_level[key] += val
                    all_level_error[key] += val

    resul_report_sorted = dict(sorted(resul_report.items()))

    if name_report:
        write_report_to_file(resul_report_sorted, all_level_error, name_report)
    else:
        write_report_to_console(resul_report_sorted, all_level_error)


def check_files(name_files: list[str]) -> bool:
    """
    Проверка наличия файлов
    :param name_files: список имен лог-файлов
    :type name_files: list[str]
    :rtype: bool
    :return: при наличии всех файлов - True, при отсутствии хотя бы одного файла - False
    """
    ls_fl: list[bool] = [os.path.isfile(name) for name in name_files]
    return all(ls_fl)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Необходимо задать входные параметры")

    name_files: list[str] = [name for name in sys.argv[1:] if name.endswith(".log")]

    if len(name_files) == 0:
        sys.exit("Не указаны лог файлы с расширением *.log")

    name_report: str | None = None
    if "--report" in sys.argv:
        if sys.argv[-2] == "--report":
            name_report = sys.argv[-1]
            if not name_report.isalnum():
                sys.exit("Имя отчета должно содержать только буквы и цифры")
        else:
            sys.exit(
                "Аргумент --report указывается в конце команды с указанием имени отчета"
            )

    if not check_files(name_files):
        sys.exit("Файл с логами не найден")

    gen_report(name_files, name_report)


if __name__ == "__main__":
    main()

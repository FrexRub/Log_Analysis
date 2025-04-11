import os.path
import sys
import re

INDEX_LEVEL_IN_LOG = 2
LEVEL_COUNT = (("debug", 0), ("info", 0), ("warning", 0), ("error", 0), ("critical", 0))


class EndpointClass:
    __slots__ = ("name_api", "count_level")

    def __init__(self, name_api: str) -> None:
        self.name_api: str = name_api
        self.count_level: dict[str, 0] = dict(LEVEL_COUNT)

    def count_error(self):
        return (self.count_level["debug"] + self.count_level["info"] +
                self.count_level["warning"] + self.count_level["error"] + self.count_level["critical"])


def read_log_file(name_file: str) -> dict[str, EndpointClass]:
    dict_endpoint: dict[str, EndpointClass] = dict()
    with open(name_file, 'r', encoding='utf-8') as file:
        for line in file:
            if "django.request" in line:
                str_log: list[str] = line.strip().split()
                level_log: str = str_log[INDEX_LEVEL_IN_LOG].lower()

                result = re.search(r"\s\/\S+", line)
                name_api: str = result.group(0)

                if dict_endpoint.get(name_api) is None:
                    dict_endpoint[name_api]: EndpointClass = EndpointClass(name_api)
                    dict_endpoint[name_api].count_level[level_log] += 1
                else:
                    dict_endpoint[name_api].count_level[level_log] += 1


        return dict_endpoint


def gen_report(name_files: list[str], name_report: str):
    slot_report: dict[str, dict[str, EndpointClass]] = dict()
    log_endpoint: dict[str, EndpointClass] = read_log_file(name_files[0])

    for key, val in log_endpoint.items():
        print("key:", key)
        for key_l, val_l in val.count_level.items():
            print("level:", key_l, "count:", val_l)


def check_files(name_files: list[str]) -> bool:
    ls_fl: list[bool] = [os.path.isfile(name) for name in name_files]
    return all(ls_fl)


def main():
    #    ['main.py', 'logs/app1.log', 'logs/app2.log', 'logs/app3.log', '--report', 'handlers']
    if len(sys.argv) < 2:
        sys.exit("Необходимо задать входные параметры")

    name_files: list[str] = [name for name in sys.argv[1:] if name.endswith(".log")]

    if len(name_files) == 0:
        sys.exit("Не указаны лог файлы с расширением *.log")

    name_report: str = "handlers"
    if "--report" in sys.argv:
        if sys.argv[-2] == "--report":
            name_report: str = sys.argv[-1]
        else:
            sys.exit("Аргумент --report указывается в конце команды с указанием имени отчета")

    if not check_files(name_files):
        sys.exit("Файл с логами не найден")

    gen_report(name_files, name_report)


if __name__ == "__main__":
    main()

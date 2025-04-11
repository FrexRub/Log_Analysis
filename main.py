import sys


def gen_report(name_files: list[str], name_report: str):
    pass


def main():
    #    ['main.py', 'logs/app1.log', 'logs/app2.log', 'logs/app3.log', '--report', 'handlers']
    if len(sys.argv) < 2:
        sys.exit("Необходимо задать входные параметры")

    name_files: list[str] = [name for name in sys.argv[1:] if name.endswith(".log")]
    print(name_files)

    if len(name_files) == 0:
        sys.exit("Не указаны лог файлы с расширением *.log")

    name_report: str = "handlers"
    if "--report" in sys.argv:
        if sys.argv[-2] == "--report":
            name_report: str = sys.argv[-1]
        else:
            sys.exit("Аргумент --report указывается в конце команды с указанием имени отчета")

    gen_report(name_files, name_report)


if __name__ == "__main__":
    main()

# Эмулятор командной строки ОС

## 1. Общее описание
Эмулятор языка оболочки ОС, имитирующий работу в командной строке
UNIX-подобной ОС. Программа работает с виртуальной файловой системой (VFS),
загружаемой из XML-файла в оперативную память, и поддерживает выполнение
скриптов и базовых файловых операций без реальной модификации файловой
системы хоста.

Вариант 12: rev, history, find (этап 4), rm (этап 5).

Учебное заведение: РТУ МИРЭА
Дисциплина: Конфигурационное управление
Группа: ИКБО-63-25
Студент: Коржаев Арсений
Язык реализации: Python 3.10+, Tkinter (GUI)

## 2. Описание всех функций и настроек

Параметры командной строки:
- --vfs-path — путь к физическому расположению VFS (XML-файл).
- --script — путь к стартовому скрипту.

Поддерживаемые команды:
- ls [путь] — содержимое директории.
- cd [путь] — переход в директорию.
- pwd — показать текущую директорию.
- cat <файл> — вывести содержимое файла.
- rev <файл> — вывести содержимое файла в обратном порядке.
- history — показать историю введённых команд.
- find <имя> — найти файл или папку по имени (рекурсивно).
- rm <путь> — удалить файл или пустую папку (только в памяти).
- help — список команд.
- exit — завершение работы.

## 3. Запуск и тесты по этапам

python src/main.py --vfs-path vfs_data/default.xml
python src/main.py --vfs-path vfs_data/default.xml --script scripts/test.txt

Через Makefile:
make run
make test

Через скрипты запуска:
./run.sh --vfs-path vfs_data/default.xml --script scripts/test.txt

Аналогичный run.bat есть для Windows.

Тесты:
python -m unittest discover tests -v

## 4. Примеры использования

Заголовок окна содержит имя VFS:
Эмулятор оболочки - MyVFS

Парсер кавычек и ошибки:
> ls "моя папка"
Заглушка: 'ls' с аргументами: ['моя папка']
> unknown
Ошибка: команда 'unknown' не найдена.

Раскрытие переменных окружения:
> cd $HOME
Заглушка: 'cd' с аргументами: ['C:\Users\User']

Команды этапа 3 (работа с VFS):
> pwd
/
> ls
  etc/
  home/
  motd.txt
> cd /home/user
> pwd
/home/user
> ls
  notes.txt
  readme.txt
> cat readme.txt
Это тестовый файл в VFS.

Команды этапа 4:
> rev /home/user/readme.txt
.ВFS в йалф йовотэт этО
> history
1 pwd
2 ls
3 cd /home/user
...
> find readme.txt
/home/user/readme.txt
> find nonexistent
Не найдено: nonexistent

Команда этапа 5:
> ls /home/user
  notes.txt
  readme.txt
> rm /home/user/notes.txt
Удалено: /home/user/notes.txt
> ls /home/user
  readme.txt
> rm /home/user/nonexistent.txt
Ошибка: не найдено: /home/user/nonexistent.txt
> rm /home
Ошибка: директория не пуста: /home

Стартовый скрипт печатает и ввод, и вывод; поддерживает комментарии (#),
строки, начинающиеся с #, игнорируются.

## 5. Структура репозитория

config-management-shell-emulator/
├── src/
│ ├── __init__.py
│ └── main.py
├── tests/
│ ├── __init__.py
│ └── test_parser.py
├── scripts/
│ └── test.txt
├── vfs_data/
│ ├── default.xml
│ └── minimal.xml
├── run.sh
├── run.bat
├── Makefile
├── .gitignore
└── README.md


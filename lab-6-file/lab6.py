import os
import logging
from functools import wraps

class FileNotFound(Exception):
    pass

class FileCorrupted(Exception):
    pass

class DuplicateTextError(Exception):
    pass

def logged(exception_type, mode="console"):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except exception_type as e:
                logger = logging.getLogger(func.__name__)
                logger.setLevel(logging.ERROR)

                if mode == "file":
                    handler = logging.FileHandler("log.txt", encoding="utf-8")
                else:
                    handler = logging.StreamHandler()

                formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
                handler.setFormatter(formatter)
                logger.addHandler(handler)

                logger.error(f"{exception_type.__name__}: {e}")
                raise
        return wrapper
    return decorator

class TextFileHandler:
    def __init__(self, filepath):
        self.filepath = filepath
        folder = os.path.dirname(filepath)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)

        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8"):
                pass

    @logged(FileCorrupted, mode="console")
    def read(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            raise FileCorrupted("Помилка читання файлу")

    @logged(FileCorrupted, mode="file")
    def write(self, content):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            raise FileCorrupted("Помилка запису у файл")

    @logged(FileCorrupted, mode="file")
    def append(self, content):
        try:
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            raise FileCorrupted("Помилка дописування у файл")

    @logged(DuplicateTextError, mode="console")
    def append_unique(self, content):
        current = self.read()
        if content.strip() in current:
            raise DuplicateTextError("Цей текст уже існує у файлі!")
        self.append(content)

    @logged(FileCorrupted, mode="file")
    def read_and_save(self):

        content = self.read()
        self.append("\nlol\n")
        self.append(content)
        return content

if __name__ == "__main__":
    fm = TextFileHandler("data/example.txt")

    try:
        fm.append_unique("44.\n")
        fm.append_unique("Олена Ступ.\n")
        fm.append_unique("Щемапец лев.\n")
        fm.append_unique("hocu zhutu.\n")
        fm.append_unique("hocu zhutueeeee.\n")
    except DuplicateTextError as e:
        print("Помилка:", e)

    print("\nВміст файлу:")
    print(fm.read_and_save())

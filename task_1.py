from pathlib import Path
from queue import Queue
from collections import UserDict
import hashlib
import argparse


class File:
    def __init__(self, path: Path, dist_path: Path) -> None:
        self.path = path
        self.dist_path = dist_path
        self.name = self.path.name
        self.__get_hash()
        self.ext = self.path.suffix.replace(".", "__")
        self.__set_backup_path()

    def __get_hash(self) -> None:
        with open(self.path, "rb") as f:
            self.hash_number = hashlib.sha256(f.read()).hexdigest()

    def __set_backup_path(self) -> None:
        self.backup_path = Path(f"{self.dist_path}/{self.ext}/{self.name}")


class FileBase(UserDict):
    def __init__(self) -> None:
        super().__init__()
        self.q_file = Queue()
        self.data = dict()

    def add_record(self, file: object) -> None:
        if file not in self.data:
            self.data[file.hash_number] = file.name
            self.q_file.put(file)


def parse_argv():
    parser = argparse.ArgumentParser(description="Копіює файли в папку")
    parser.add_argument(
        "-r", "--root", type=Path, required=True, help="Папка з файлами"
    )
    parser.add_argument(
        "-d", "--dist", type=Path, default=Path("dist"), help="Папка для копіювання"
    )
    return parser.parse_args()


def scan_tree(path: Path, dist_path: Path) -> None:
    if path.is_file():
        file = File(path, dist_path)
        db.add_record(file)
    if path.is_dir():
        for child in path.iterdir():
            scan_tree(child, dist_path)


def copy_files():
    if not db.q_file.empty():
        file = db.q_file.get()
        try:
            file.backup_path.parent.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            print(f"File {file.backup_path} already exists")
        try:
            file.backup_path.write_bytes(file.path.read_bytes())
        except PermissionError:
            print(
                f"Permission denied. You can't copy {file.path} to {file.backup_path}"
            )
        copy_files()


def main():
    args = parse_argv()
    root = args.root
    dist_path = args.dist
    if dist_path == Path("dist"):
        dist_path = Path(f"{root}/{dist_path}")
    scan_tree(Path(root), Path(dist_path))
    copy_files()


if __name__ == "__main__":
    db = FileBase()
    main()

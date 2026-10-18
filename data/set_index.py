import json
from pathlib import Path
from tempfile import NamedTemporaryFile


class SetIndex:
    """Remember page titles and product codes independently of list order."""

    def __init__(self, path: Path):
        self.path = path
        if path.is_file():
            with path.open(encoding="utf-8") as source:
                self._codes = json.load(source)
            if not isinstance(self._codes, dict) or not all(
                isinstance(title, str) and isinstance(code, str)
                for title, code in self._codes.items()
            ):
                raise ValueError(f"Invalid set index: {path}")
        else:
            self._codes = {}

    def get(self, title: str) -> str | None:
        return self._codes.get(title.strip())

    def remember(self, title: str, code: str):
        title = title.strip()
        code = code.strip().upper()
        if self._codes.get(title) == code:
            return

        codes = {**self._codes, title: code}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None
        try:
            with NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.path.parent,
                prefix=".set_index-", suffix=".tmp", delete=False,
            ) as output:
                temporary_path = Path(output.name)
                json.dump(codes, output, indent=4, ensure_ascii=False)
                output.write("\n")
            temporary_path.replace(self.path)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
        self._codes = codes

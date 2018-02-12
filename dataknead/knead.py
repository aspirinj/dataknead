import csv, json
from pathlib import Path

class Knead:
    SUPPORTED_TYPES = ("csv", "json")
    type = None
    data = None

    def __init__(self, inp, filetype = None):
        if isinstance(inp, str):
            # We assume this is a path, load the data
            # If we have a filetype forced, use that, otherwise get it from
            # the file extension
            if filetype:
                self.type = filetype
            else:
                self.type = self._get_filetype(inp)

            self._load(inp)
        else:
            # We assume this is data, assign it
            self.type = type(inp).__name__
            self._data = inp

    def _get_filetype(self, path):
        filetype = Path(path).suffix[1:]

        if filetype not in self.SUPPORTED_TYPES:
            raise Exception("Unsupported file type: %s" % self.type)
        else:
            return filetype

    def _load(self, pathstr):
        with open(pathstr) as f:
            if self.type == "json":
                self._data = json.loads(f.read())
            elif self.type == "csv":
                reader = csv.DictReader(f)
                self._data = [row for row in reader]

    def data(self):
        return self._data

    def _write_csv(self, path, fieldnames = None):
        data = self.data()

        # First extract all the fieldnames from the list
        if not fieldnames:
            fieldnames = set()
            for item in data:
                [fieldnames.add(key) for key in item.keys()]

        # Then open the CSV file and write
        with open(path, "w") as f:
            writer = csv.DictWriter(f, fieldnames = fieldnames)
            writer.writeheader()
            [writer.writerow(row) for row in data]

    def _write_json(self, path, indent = None):
        with open(path, "w") as f:
            jsondata = json.dumps(self.data(), indent = indent)
            f.write(jsondata)

    def write(self, path, indent = None, fieldnames = None):
        filetype = self._get_filetype(path)

        if filetype == "json":
            self._write_json(path, indent)
        elif filetype == "csv":
            self._write_csv(path, fieldnames)
import json
from io import StringIO
from jq import jq
from pathlib import Path
from .loaders.csvloader import CsvLoader
from .loaders.jsonloader import JsonLoader
from .loaders.textloader import TextLoader

class Knead:
    loaders = [JsonLoader, CsvLoader, TextLoader]

    _data = None

    def __init__(self, inp, parse_as = None, read_as = None, is_data = False, **kwargs):
        if parse_as:
            # Process string like file
            if not isinstance(inp, str):
                raise TypeError("Input needs to be string, not %s" % type(inp).__name__)

            loader = self._get_loader(parse_as)
            f = StringIO(inp)
            self._data = loader.read(f, **kwargs)
        elif isinstance(inp, str) and not is_data:
            # Either a path or a stringified data file
            if not read_as:
                read_as = Path(inp).suffix[1:]

            loader = self._get_loader(read_as)

            with open(inp) as f:
                self._data = loader.read(f, **kwargs)
        else:
            # We assume this is parsed data, assign it
            self._data = inp

    def __repr__(self):
        return json.dumps(self.data(), indent = 4)

    def __str__(self):
        return json.dumps(self.data(), indent = 4)

    def _get_loader(self, extension):
        for loader in self.loaders:
            if extension in loader.EXTENSION:
                return loader

        raise Exception("Could not find loader for type '%s'" % extension)

    def apply(self, fn):
        """
        Runs a function over the data
        """
        self._data = fn(self.data())
        return self


    def data(self, check_instance = None):
        datatype = type(self._data)

        if check_instance and not isinstance(self._data, check_instance):
            raise Exception(
                "Data of type %s can not be processed, needs to be %s" %
                ( datatype.__name__, check_instance.__name__)
            )

        return self._data

    def filter(self, fn):
        data = [row for row in self.data(check_instance = list) if fn(row)]
        return Knead(data)

    def keys(self):
        return Knead(list(self.data().keys()))

    def map(self, iteratee):
        data = self.data(check_instance = list)

        # If 'iteratee' is a function, map over the data
        if callable(iteratee):
            data = [iteratee(row) for row in data]
        # Shortcut, like 'pluck'
        elif isinstance(iteratee, str):
            data = [row[iteratee] for row in data]
        # Another shortcut, for mulitple keys
        elif isinstance(iteratee, tuple):
            data = [ { key:row[key] for key in iteratee } for row in data ]
        else:
            raise TypeError("Iteratee should be of type dict or function")

        return Knead(data)

    # This is basically a wrapper around jq
    def query(self, query, default = None):
        try:
            result = jq(query).transform(self.data(), multiple_output = True)
        except:
            return Knead(default, is_data = True)

        # jq.py has this weird habit of not returning a list when there
        # are multiple outputs, *however* when we set multiple_output = True,
        # every result is a list, so we check here if the result is a list
        # with just *one* item, and if so, just return the first item in that
        # list
        if (isinstance(result, list) and len(result) == 1):
            result = result[0]

        if not result and default:
            return default
        else:
            return Knead(result, is_data = True)

    def values(self):
        return Knead(list(self.data().values()))

    def write(self, path, write_as = None, **kwargs):
        if not write_as:
            write_as = Path(path).suffix[1:]

        loader = self._get_loader(write_as)

        with open(path, "w") as f:
            loader.write(f, self.data(), **kwargs)
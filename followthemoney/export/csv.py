import csv
from pathlib import Path

from followthemoney.export.common import Exporter


class CSVExporter(Exporter):
    def __init__(self, directory, dialect=csv.unix_dialect, extra=None):
        self.directory = Path(directory)
        self.dialect = dialect
        self.extra = extra or []
        self.handles = {}

    def _write_header(self, writer, schema):
        headers = ['id']
        headers.extend(self.extra)
        for prop in schema.sorted_properties:
            # Not using label to make it more machine-readable:
            headers.append(prop.name)
        writer.writerow(headers)

    def _open_csv_file(self, name):
        self.directory.mkdir(parents=True, exist_ok=True)
        file_path = self.directory.joinpath('{0}.csv'.format(name))
        handle = open(file_path, mode='w')
        writer = csv.writer(handle, dialect=self.dialect)
        return handle, writer

    def _get_writer(self, schema):
        if schema not in self.handles:
            handle, writer = self._open_csv_file(schema.name)
            self.handles[schema] = (handle, writer)
            self._write_header(writer, schema)
        handle, writer = self.handles[schema]
        return writer

    def write(self, proxy, extra=None):
        writer = self._get_writer(proxy.schema)
        cells = [proxy.id]
        cells.extend(extra or [])
        for prop in proxy.schema.sorted_properties:
            cells.append(prop.type.join(proxy.get(prop)))

        writer.writerow(cells)

    def finalize(self):
        for (handle, writer) in self.handles.values():
            handle.close()

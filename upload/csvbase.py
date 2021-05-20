import logging, re

from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


def empty_updater(*args, **kwargs):
  pass


class GenericLoader:
  KEY_FIELDS = []
  FIELDS = []
  """
    CSV uploader, abstract base class.  How to extend:

    class ThingLoader(GenericLoader):

      KEY_FIELDS = ["key"]
      FIELDS = ["f1", "f2", "f3"]
      MODEL_CLASS = Thing

      def _map_data(self, data):
        keys = {}
        fields = {}
        keys["key"] = data["a"]
        fields["f1"] = data["b"]
        fields["f2"] = data["c"]
        fields["f3"] = data["d"]
        return keys, fields
  """
  @staticmethod
  def normalize_header(header):
    header = re.sub(r"""[^a-zA-Z0-9]+""", " ", header)
    return header.strip().lower()

  def __init__(self, reader, *args, **kwargs):
    self.reader = reader
    self.kwargs = kwargs

  def process(self, updater=empty_updater):
    self.objects_added = []
    self.objects_updated = []
    self.errors = []
    self.mappings = None
    row_index = -1
    rows_processed = 0

    keep_going = True
    for row in self.reader:
      row_index += 1
      if not "".join(row):  # Ignore empty rows
        continue
      try:
        if not self.mappings:
          self._map_headers(row)
        else:
          rows_processed += 1
          obj, created = self._process_row(row)
          if created:
            self.objects_added.append(obj)
          else:
            self.objects_updated.append(obj)
      except ValidationError as e:
        for msg in iter(e):
          self.errors.append(f"row {row_index + 1}: {str(msg)}")
        keep_going = self.mappings is not None
      except ValueError as e:
        self.errors.append(f"row {row_index + 1}: {str(e)}")
        keep_going = self.mappings is not None
      updater(status="running" if keep_going else "error",
              rows_processed=rows_processed,
              objects_added=len(self.objects_added),
              objects_updated=len(self.objects_updated),
              errors=self.errors)
      if not keep_going:
        return
    updater(status="done",
            rows_processed=rows_processed,
            objects_added=len(self.objects_added),
            objects_updated=len(self.objects_updated),
            errors=self.errors)

  def _process_row(self, row):
    data = {}
    for f in self.KEY_FIELDS + self.FIELDS:
      data[f] = row[self.mappings[f]] if self.mappings[f] < len(row) else ""
    keys, fields = self._map_data(data)
    return (self.MODEL_CLASS).objects.update_or_create(**keys, defaults=fields)

  def _map_headers(self, row):
    mappings = {}
    for idx, val in enumerate(row):
      h = self.normalize_header(val)
      if h in self.KEY_FIELDS + self.FIELDS:
        mappings[h] = idx

    # Check that all fields are present.
    missing_fields = []
    for field_name in self.FIELDS:
      if field_name not in mappings:
        missing_fields.append(field_name)
    if missing_fields:
      raise ValidationError("The data file is missing required %s field%s." %
                            (", ".join(missing_fields), "s" if len(missing_fields) != 1 else ""))
    self.mappings = mappings

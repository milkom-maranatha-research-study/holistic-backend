import csv

from django.http import StreamingHttpResponse
from itertools import chain


class Echo:
    """
    An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """
        Write the value by returning it, instead of storing in a buffer.
        """
        return value


class CSVStream:
    """
    Class to stream (download) an iterator to a CSV file.
    """
    def export(self, filename, headers, iterator, serializer_class):
        # 1. Create our writer object with the pseudo buffer
        writer = csv.writer(Echo())

        # 2. Create the StreamingHttpResponse using our iterator as streaming content
        serializer = serializer_class()

        response = StreamingHttpResponse(
            chain((writer.writerow(headers)), (writer.writerow(serializer.to_representation(data)) for data in iterator)),
            content_type="text/csv"
        )

        # 3. Add additional headers to the response
        response['Content-Disposition'] = f"attachment; filename={filename}.csv"

        # 4. Return the response
        return response

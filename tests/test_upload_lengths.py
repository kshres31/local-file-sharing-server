import io
import unittest
from unittest.mock import Mock, patch

from lan_drop.server import Handler


class UploadLengthTests(unittest.TestCase):
    def handler(self, length, body=b"hello"):
        handler = object.__new__(Handler)
        handler.path = "/files/example.txt"
        handler.headers = {"Content-Length": str(length)}
        handler.rfile = Mock(wraps=io.BytesIO(body))
        handler.send_json = Mock()
        return handler

    def test_negative_length_is_rejected_without_reading_or_saving(self):
        handler = self.handler(-1)
        with patch("lan_drop.server.STORAGE") as storage:
            storage.max_bytes = 5
            handler.do_PUT()
            handler.rfile.read.assert_not_called()
            storage.save.assert_not_called()
        self.assertEqual(handler.send_json.call_args.args[0], 400)

    def test_oversized_length_is_rejected_without_reading(self):
        handler = self.handler(6)
        with patch("lan_drop.server.STORAGE") as storage:
            storage.max_bytes = 5
            handler.do_PUT()
            handler.rfile.read.assert_not_called()
            storage.save.assert_not_called()
        self.assertEqual(handler.send_json.call_args.args[0], 400)

    def test_empty_and_limit_sized_uploads_are_accepted(self):
        for body in (b"", b"hello"):
            with self.subTest(size=len(body)):
                handler = self.handler(len(body), body)
                with patch("lan_drop.server.STORAGE") as storage:
                    storage.max_bytes = 5
                    storage.save.return_value = {"size": len(body)}
                    handler.do_PUT()
                    storage.save.assert_called_once_with("example.txt", body)
                handler.rfile.read.assert_called_once_with(len(body))
                handler.send_json.assert_called_once_with(201, {"size": len(body)})

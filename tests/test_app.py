import io
import unittest
from pathlib import Path

from app import server


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if Path(server.DB_PATH).exists():
            Path(server.DB_PATH).unlink()
        server.init_db()

    def call(self, path='/', method='GET'):
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'wsgi.input': io.BytesIO(b''),
        }
        captured = {}

        def start_response(status, headers):
            captured['status'] = status
            captured['headers'] = dict(headers)

        body = b''.join(server.app(environ, start_response))
        return captured['status'], captured['headers'], body

    def test_health(self):
        status, headers, body = self.call('/health')
        self.assertEqual(status, '200 OK')
        self.assertIn('application/json', headers['Content-Type'])
        self.assertIn(b'"ok"', body)

    def test_student_page(self):
        status, _, body = self.call('/student/1')
        self.assertEqual(status, '200 OK')
        self.assertIn(b"Today's Lesson Queue", body)


if __name__ == '__main__':
    unittest.main()

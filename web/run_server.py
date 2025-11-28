from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_GET(self):
        # Разрешаем доступ к файлам
        if self.path.startswith('/web/') or self.path == '/web':
            self.path = self.path[1:]  # Убираем начальный /
        else:
            self.path = '/web/app.html'
        return super().do_GET()

def run(server_class=HTTPServer, handler_class=CORSRequestHandler, port=8001):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"🌍 Локальный сервер запущен: http://localhost:{port}")
    print("👉 Используй ngrok, чтобы открыть доступ из интернета")
    httpd.serve_forever()

if __name__ == '__main__':
    os.chdir('.')  # корень проекта
    run(port=8001)
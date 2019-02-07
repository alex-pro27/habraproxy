import re
import urllib3
from http.server import HTTPServer, BaseHTTPRequestHandler


class HTTPRequestHandler(BaseHTTPRequestHandler):

    http = urllib3.PoolManager()

    def do_GET(self):
        """ Обработка GET запросов """
        content, content_type, status = self.__get_content()
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.send_header("Content-Length", len(content))
        self.end_headers()
        self.wfile.write(content)

    def __get_content(self):
        """ Получить контент с хабра """
        habr = "https://habr.com"
        server = "http://{0}:{1}".format(*self.server.server_address)
        response = self.http.request("GET", habr + self.path)
        content_type = response.headers.get("Content-Type")
        content = response.data

        if "html" in content_type:
            encoding = re.findall(r"charset=(.+)", content_type)[0]
            text = content.decode(encoding).replace(habr, server)
            articles = re.findall('<article[^>]*>[\w\W]+</article>', text)
            for article in articles:
                new_article = re.sub(r"(?<=\s)([\w]{6})(?=\b)(?![^<]+>)", '\\1™', article)
                text = text.replace(article, new_article)
                content = bytes(text, encoding)
        return content, content_type, response.status


class Server:

    def __init__(self, host, port):
        self.server = HTTPServer((host, port), HTTPRequestHandler)

    def start(self):
        print("Server started. http://{0}:{1}".format(*self.server.server_address))
        self.server.serve_forever()

    def stop(self):
        self.__del__()

    def __del__(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()


if __name__ == "__main__":
    server = Server("127.0.0.1", 8888)
    server.start()
    server.stop()

"""Servidor e regras do jogo da velha, usando apenas a biblioteca padrão."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path(__file__).resolve().parent
LINHAS = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7),
          (2, 5, 8), (0, 4, 8), (2, 4, 6))


def avaliar(tabuleiro):
    for a, b, c in LINHAS:
        if tabuleiro[a] and tabuleiro[a] == tabuleiro[b] == tabuleiro[c]:
            return {"vencedor": tabuleiro[a], "linha": [a, b, c], "empate": False}
    return {"vencedor": None, "linha": [], "empate": all(tabuleiro)}


class Servidor(BaseHTTPRequestHandler):
    def do_GET(self):
        arquivos = {"/": ("index.html", "text/html; charset=utf-8"),
                    "/style.css": ("style.css", "text/css; charset=utf-8")}
        if self.path not in arquivos:
            self.send_error(404)
            return
        nome, tipo = arquivos[self.path]
        conteudo = (BASE / nome).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(conteudo)))
        self.end_headers()
        self.wfile.write(conteudo)

    def do_POST(self):
        if self.path != "/avaliar":
            self.send_error(404)
            return
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            if not 0 < tamanho <= 1024:
                raise ValueError("Requisição inválida")
            tabuleiro = json.loads(self.rfile.read(tamanho))["tabuleiro"]
            if not isinstance(tabuleiro, list) or len(tabuleiro) != 9 or any(
                celula not in ("", "X", "O") for celula in tabuleiro
            ):
                raise ValueError("Tabuleiro inválido")
            resposta = json.dumps(avaliar(tabuleiro)).encode("utf-8")
        except (ValueError, TypeError, KeyError, json.JSONDecodeError):
            self.send_error(400, "Tabuleiro inválido")
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(resposta)))
        self.end_headers()
        self.wfile.write(resposta)


def iniciar(porta=8000):
    servidor = ThreadingHTTPServer(("127.0.0.1", porta), Servidor)
    print(f"Jogo disponível em http://localhost:{porta} (Ctrl+C para parar)", flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()

#!/usr/bin/env python3
import json
import os
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class CardEditorHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/api/decks':
            return self.handle_get_decks()
        elif parsed.path == '/api/card':
            return self.handle_get_card(parsed.query)
        elif parsed.path == '/api/cards':
            query = parse_qs(parsed.query)
            deck = query.get('deck', [''])[0]
            subdeck = query.get('subdeck', [''])[0]
            return self.handle_get_cards(deck, subdeck)
        elif parsed.path == '/api/repo-path':
            return self.handle_get_repo_path()
        else:
            return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == '/api/card':
            return self.handle_save_card()
        elif parsed.path == '/api/upload-image':
            return self.handle_upload_image()
        else:
            self.send_error(404)

    def handle_get_decks(self):
        try:
            with open('decks.json', 'r') as f:
                data = json.load(f)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def handle_get_card(self, query):
        try:
            params = parse_qs(query)
            card_id = params.get('id', [''])[0]

            if not card_id:
                self.send_error(400, "Missing card id")
                return

            # Find card in cards directory
            cards_dir = Path('cards')
            for card_file in cards_dir.rglob('*.json'):
                with open(card_file, 'r') as f:
                    card = json.load(f)
                    if card.get('id') == card_id:
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps(card).encode())
                        return

            self.send_error(404, f"Card {card_id} not found")
        except Exception as e:
            self.send_error(500, str(e))

    def handle_get_cards(self, deck, subdeck):
        try:
            cards_list = []
            cards_dir = Path('cards')

            for card_file in cards_dir.rglob('*.json'):
                with open(card_file, 'r') as f:
                    card = json.load(f)
                    if card.get('deck') == deck and card.get('subdeck') == subdeck:
                        cards_list.append({
                            'id': card['id'],
                            'title': card['title'],
                            'tags': card.get('tags', []),
                            'view': card.get('view', ''),
                        })

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(cards_list).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def handle_save_card(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            card_data = json.loads(body.decode())

            # Save to cards/{deck}/{subdeck}/{id}.json
            deck = card_data.get('deck', '')
            subdeck = card_data.get('subdeck', '')
            card_id = card_data.get('id', '')

            if not all([deck, subdeck, card_id]):
                self.send_error(400, "Missing deck, subdeck, or id")
                return

            card_path = Path(f'cards/{deck}/{subdeck}/{card_id}.json')
            card_path.parent.mkdir(parents=True, exist_ok=True)

            with open(card_path, 'w') as f:
                json.dump(card_data, f, indent=2)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def handle_get_repo_path(self):
        try:
            repo_path = os.getcwd()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'path': repo_path}).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def handle_upload_image(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'No file provided'}).encode())
                return

            # Read file data
            body = self.rfile.read(content_length)

            # Get the destination path from query params
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            dest_path = query.get('path', [''])[0]

            if not dest_path:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing destination path'}).encode())
                return

            # Validate path is within repo
            repo_path = Path.cwd()
            full_path = (repo_path / dest_path).resolve()

            if not str(full_path).startswith(str(repo_path)):
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Path outside repository'}).encode())
                return

            # Create directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(full_path, 'wb') as f:
                f.write(body)

            # Return relative path with forward slashes
            rel_path = str(full_path.relative_to(repo_path)).replace('\\', '/')
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'path': rel_path}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(('localhost', 8000), CardEditorHandler)
    print("Card Editor running at http://localhost:8000")
    print("Press Ctrl+C to stop")
    server.serve_forever()

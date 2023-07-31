import requests
import json
import sys
import bech32
from base64 import b64decode
from concurrent.futures import ThreadPoolExecutor

import socket
import datetime
import threading

def fetchValopers(coin):
	headers = {
			'User-Agent': 'Go-http-client/1.1',
			'Content-Type': 'application/json'
	}

	data = {
			"jsonrpc": "2.0",
			"id": 0,
			"method": "abci_query",
			"params": {
					"data": "0A"+(format(len(coin), '02x')+bytes.hex(coin.encode())).upper(),
					"height": "0",
					"path": "/axelar.nexus.v1beta1.QueryService/ChainMaintainers",
					"prove": False
			}
	}

	addrs = []
	response = requests.post(config['rpc'], headers=headers, data=json.dumps(data))
	print(response.text)
	value = json.loads(response.text)['result']['response']['value']
	decoded = b64decode(value)
	while len(decoded) > 0:
		addrs.append(decoded[2:20+2])
		decoded = decoded[22:]
	decoded = [bech32.bech32_encode("axelarvaloper", bech32.convertbits(addr, frombits=8, tobits=5)) for addr in addrs]
	return decoded

def maintains(valoper, coin):
	valopers = fetchValopers(coin)
	return any([valoper == valop for valop in valopers])

class MetricsServer:
	def __init__(self, host = 'localhost', port = 8080):
		self.host = host
		self.port = port

	def handle_client(self, client_socket):
		request = client_socket.recv(1024)

		if 'GET /metrics' in request.decode():
			http_response = self.create_http_response()
			client_socket.send(http_response.encode())
		else:
			client_socket.send(b'HTTP/1.1 404 NOT FOUND\r\n\r\nPage not found')
		client_socket.close()

	def create_http_response(self):
		http_response = """HTTP/1.1 200 OK
Content-Type: text/plain

# HELP evm_chain_registered 2 if registered, 1 if don't know, 0 if not registered
# TYPE evm_chain_registered gauge"""

		def fetch_result(chain):
			try:
				return chain, {True: 2, False: 0}[maintains(config['watch'], chain)]
			except:
				return chain, 1

		with ThreadPoolExecutor() as executor:
			results = executor.map(fetch_result, config['chains'])

		for chain, result in results:
			http_response += f"\nevm_chain_registered{{chain=\"{chain}\",valoper=\"{config['watch']}\"}} {result}"
		http_response += "\n"

		return http_response

	def start(self):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.bind((self.host, self.port))
		server.listen(5)
		print(f"[*] Listening on {self.host}:{self.port}")

		while True:
			client, addr = server.accept()
			print(f"[*] Accepted connection from: {addr[0]}:{addr[1]}")
			client_handler = threading.Thread(target=self.handle_client, args=(client,))
			client_handler.start()


if __name__ == "__main__":
	try:
		config = json.loads(open("config.json","rb").read().decode())
	except FileNotFoundError:
		print("Coult not find config.json. Exiting.")
		sys.exit(1)
	metrics_server = MetricsServer(host=config['host'], port=config['port'])
	metrics_server.start()

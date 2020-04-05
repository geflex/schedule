import socket
import time


class SocketBenchmark:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.conn = socket.create_connection((self.host, self.port))

    def send(self, text):
        text = text + '\n'
        self.conn.send(text.encode())

    def read(self):
        return self.conn.recv()

    def load(self, rps, *, rcount=float('inf'), runtime=float('inf')):
        print(f'rps={rps}')
        sleeptime = 1/rps
        if runtime:
            print(f'with runtime={runtime}')
            rcount = int(runtime/sleeptime)
        else:
            print(f'with rcount={rcount}')

        for i in range(0, rcount):
            msg = f'Прив че дел {i}'
            print(f'sended {repr(msg)}')
            self.send(msg)
            time.sleep(sleeptime)


if __name__ == '__main__':
    SocketBenchmark().load(rps=2, runtime=10)

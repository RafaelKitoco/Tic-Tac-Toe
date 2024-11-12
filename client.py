import tkinter as tk
import socket
import threading

class TicTacToe:
    def __init__(self, root, n, win_sequence, socket=None):
        self.root = root
        self.n = n
        self.win_sequence = win_sequence
        self.board = [['' for _ in range(n)] for _ in range(n)]
        self.players = ["X", "O"]
        self.turn = 0
        self.winner = None
        self.socket = socket
        self.create_board()

    def create_board(self):
        for i in range(self.n):
            for j in range(self.n):
                button = tk.Button(self.root, text='', width=10, height=3, 
                                   command=lambda i=i, j=j: self.play(i, j))
                button.grid(row=i, column=j)
        self.status_label = tk.Label(self.root, text="Current player: " + self.players[self.turn])
        self.status_label.grid(row=self.n, column=0, columnspan=self.n)

    def play(self, i, j):
        if self.winner is None and self.board[i][j] == '':
            self.board[i][j] = self.players[self.turn]
            self.update_board()

            if self.check_winner(i, j):
                self.status_label.config(text="Player " + self.players[self.turn] + " wins!")
                self.winner = self.players[self.turn]
                self.show_restart_button()
                self.send_message(f'win {self.players[self.turn]}')
            elif self.check_draw():
                self.status_label.config(text="It's a draw!")
                self.winner = "Draw"
                self.show_restart_button()
                self.send_message('draw')
            else:
                self.turn = (self.turn + 1) % len(self.players)
                self.status_label.config(text="Current player: " + self.players[self.turn])
                if self.socket:
                    self.send_message(f'move {i} {j}')

    def update_board(self):
        for i in range(self.n):
            for j in range(self.n):
                button = self.root.grid_slaves(row=i, column=j)[0]
                button.config(text=self.board[i][j])

    def check_winner(self, x, y):
        player = self.board[x][y]
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1
            for d in [1, -1]:
                nx, ny = x, y
                while True:
                    nx += dx * d
                    ny += dy * d
                    if 0 <= nx < self.n and 0 <= ny < self.n and self.board[nx][ny] == player:
                        count += 1
                    else:
                        break
                if count >= self.win_sequence:
                    return True
        return False

    def check_draw(self):
        for row in self.board:
            if '' in row:
                return False
        return True

    def show_restart_button(self):
        restart_button = tk.Button(self.root, text="Play Again", command=self.restart_game)
        restart_button.grid(row=self.n + 1, column=0, columnspan=self.n)

    def restart_game(self):
        self.board = [['' for _ in range(self.n)] for _ in range(self.n)]
        self.turn = 0
        self.winner = None
        self.update_board()
        self.status_label.config(text="Current player: " + self.players[self.turn])

    def send_message(self, message):
        if self.socket:
            self.socket.send(message.encode())

    def receive_message(self):
        if self.socket:
            return self.socket.recv(1024).decode()

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))

    root = tk.Tk()
    tic_tac_toe = TicTacToe(root, 3, 3, client_socket)

    def listen_to_server():
        while True:
            message = tic_tac_toe.receive_message()
            if message.startswith('move'):
                _, i, j = message.split()
                tic_tac_toe.play(int(i), int(j))
            elif message in ['win', 'draw']:
                tic_tac_toe.status_label.config(text="Game over: " + message)

    threading.Thread(target=listen_to_server, daemon=True).start()

    root.mainloop()
    client_socket.close()

start_client()
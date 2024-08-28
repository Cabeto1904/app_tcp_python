import tkinter as tk
from tkinter import simpledialog
import socket
import threading
from queue import Queue


class PrincipalSrv:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Servidor")

        self.btn_launch = tk.Button(self.root, text="INICIAR SERVIDOR", font=(
            "Segoe UI", 14), command=self.btn_launch_action)
        self.btn_launch.grid(row=1, column=0, padx=10, pady=10)

        self.j_label1 = tk.Label(
            self.root, text="SERVIDOR TCP:", font=("Tahoma", 18), fg="red")
        self.j_label1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.message_txt = tk.Text(
            self.root, state="disabled", width=50, height=15)
        self.message_txt.grid(row=2, column=0, padx=10, pady=10)

        self.PORT = 12345
        self.connected_clients = set()
        self.client_writers = {}
        self.client_names = {"All"}

        self.server_socket = None
        self.queue = Queue()

        threading.Thread(target=self.process_queue, daemon=True).start()

        self.root.mainloop()

    def append_message(self, message):
        self.queue.put(message)

    def process_queue(self):
        while True:
            message = self.queue.get()
            self.message_txt.config(state="normal")
            self.message_txt.insert(tk.END, message + "\n")
            self.message_txt.config(state="disabled")
            self.queue.task_done()

    def btn_launch_action(self):
        server_name = simpledialog.askstring(
            "Input", "Ingrese el nombre del servidor:", parent=self.root)
        if server_name:
            self.j_label1.config(text="SERVIDOR TCP : " + server_name)
            threading.Thread(target=self.launch_server, args=(
                server_name,), daemon=True).start()
            self.btn_launch.config(state="disabled")

    def launch_server(self, server_name):
        try:
            self.server_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(("", self.PORT))
            self.server_socket.listen(5)
            addr = socket.gethostbyname(socket.gethostname())
            self.append_message(
                f"Servidor TCP en ejecución: {addr} ,Puerto {self.PORT},Nombre: {server_name}")

            while True:
                client_socket, addr = self.server_socket.accept()
                client_name = client_socket.recv(1024).decode("utf-8")
                self.client_names.add(client_name)
                self.connected_clients.add(client_socket)
                self.client_writers[client_name] = client_socket
                self.update_connected_clients()
                self.append_message(f"{client_name} se ha conectado.")

                client_socket.sendall(
                    f"{server_name}: Conexión exitosa.".encode("utf-8"))
                threading.Thread(target=self.manage_client, args=(
                    client_socket, client_name), daemon=True).start()
        except Exception as e:
            self.append_message(f"Error: {str(e)}")

    def broadcast_message(self, message):
        for client_socket in self.connected_clients:
            client_socket.sendall(message.encode("utf-8"))

    def manage_client(self, client_socket, client_name):
        try:
            while True:
                message = client_socket.recv(1024).decode("utf-8")
                if not message:
                    break

                if ":" in message:
                    target_client, client_message = message.split(":", 1)
                    client_message = f"{client_name}: {client_message.strip()}"
                    self.append_message(
                        f"{client_message}. To: {target_client}")
                    if target_client == "All":
                        self.broadcast_message(client_message)
                    else:
                        target_client_socket = self.client_writers.get(
                            target_client)
                        if target_client_socket:
                            target_client_socket.sendall(
                                client_message.encode("utf-8"))
                else:
                    self.broadcast_message(f"{client_name}: {message}")
        except Exception as e:
            self.append_message(f"Error: {str(e)}")
        finally:
            client_socket.close()
            self.client_names.remove(client_name)
            self.connected_clients.remove(client_socket)
            del self.client_writers[client_name]
            self.update_connected_clients()
            self.append_message(f"{client_name} se ha desconectado.")

    def update_connected_clients(self):
        clients = "CLIENTES:" + ",".join(self.client_names)
        for client_socket in self.connected_clients:
            client_socket.sendall(clients.encode("utf-8"))


if __name__ == "__main__":
    PrincipalSrv()

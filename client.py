import tkinter as tk
from tkinter import simpledialog, messagebox
import socket
import threading


class PrincipalCli:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cliente")

        self.PORT = 12345
        self.socket = None
        self.out = None
        self.in_ = None
        self.client_name = None

        self.init_components()
        self.root.mainloop()

    def init_components(self):
        self.connect_button = tk.Button(self.root, text="CONECTAR CON SERVIDOR", font=(
            "Segoe UI", 14), command=self.connect_button_action)
        self.connect_button.grid(
            row=1, column=0, columnspan=2, padx=10, pady=10)

        self.label = tk.Label(self.root, text="CLIENTE TCP:",
                              font=("Tahoma", 18), fg="red")
        self.label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.message_entry = tk.Entry(self.root, font=("Verdana", 14))
        self.message_entry.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.send_button = tk.Button(self.root, text="Enviar", font=(
            "Verdana", 14), command=self.send_button_action)
        self.send_button.grid(row=2, column=1, padx=10, pady=10)

        self.recipient_label = tk.Label(
            self.root, text="Destinatario:", font=("Segoe UI", 14))
        self.recipient_label.grid(row=3, column=0, padx=10, pady=10)

        self.recipient_combobox = tk.ttk.Combobox(
            self.root, font=("Segoe UI", 14))
        self.recipient_combobox.grid(
            row=3, column=1, padx=10, pady=10, sticky="ew")

        self.messages_text = tk.Text(
            self.root, state="disabled", width=50, height=15)
        self.messages_text.grid(
            row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_rowconfigure(4, weight=1)

    def connect_button_action(self):
        self.client_name = simpledialog.askstring(
            "Input", "Ingrese su nombre:", parent=self.root)
        if self.client_name:
            self.label.config(text="CLIENTE TCP : " + self.client_name)
            self.connect_to_server()
            self.connect_button.config(state="disabled")

    def connect_to_server(self):
        messagebox.showinfo("Connecting", "Conectando con servidor...")
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(("localhost", self.PORT))
            self.out = self.socket.makefile("w")
            self.in_ = self.socket.makefile("r")

            self.out.write(self.client_name + "\n")
            self.out.flush()

            threading.Thread(target=self.listen_to_server, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def listen_to_server(self):
        try:
            while True:
                from_server = self.in_.readline().strip()
                if from_server.startswith("CLIENTES:"):
                    self.update_client_list(from_server[9:])
                else:
                    self.append_message(from_server)
        except Exception as e:
            self.append_message(f"Error: {str(e)}")

    def update_client_list(self, client_list):
        self.recipient_combobox["values"] = client_list.split(",")

    def append_message(self, message):
        self.messages_text.config(state="normal")
        self.messages_text.insert(tk.END, message + "\n")
        self.messages_text.config(state="disabled")

    def send_button_action(self):
        recipient = self.recipient_combobox.get()
        if recipient:
            self.out.write(f"{recipient}:{self.message_entry.get()}\n")
            self.out.flush()
            self.message_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Seleccione un destinatario.")


if __name__ == "__main__":
    PrincipalCli()

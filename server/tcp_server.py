#!/usr/bin/env python3

import socket
import signal
import time
import threading
import serial
from datetime import datetime
import os

HOST = "0.0.0.0"
PORT = 5001

BAUD = 9600
SERIAL_PORT = "/dev/ttyACM0" 

_running = True
_lock = threading.Lock()

def handle_sig(*_):
    global _running
    _running = False

def open_serial():
    ser = serial.Serial(SERIAL_PORT, BAUD, timeout=2)
    time.sleep(2.0)  # el UNO se reinicia al abrir el puerto
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    print(f"[SERIAL] Conectado a {SERIAL_PORT} @ {BAUD}")
    return ser

def read_line(ser):
    return ser.readline().decode("utf-8", errors="ignore").strip()

def send_to_arduino(ser, cmd):
    ser.write((cmd.strip() + "\n").encode("utf-8"))
    ser.flush()
    resp = read_line(ser)
    return resp if resp else "ERR sin respuesta del Arduino"

def log(msg):
    with open("servidor_tcp.log", "a") as log_file:
        log_file.write(f"{datetime.now()} - {msg}\n")

def main():
    log("=== Iniciando servidor TCP ===")
    global _running
    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    ser = open_serial()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)
        s.settimeout(0.5)

        print(f"[TCP] Escuchando en {HOST}:{PORT}")
        log(f"[TCP] Escuchando en {HOST}:{PORT}")

        while _running:
            try:
                conn, _ = s.accept()
            except socket.timeout:
                continue

            with conn:
                conn.settimeout(1.0)
                data = b""
                try:
                    while True:
                        chunk = conn.recv(1024)
                        if not chunk:
                            break
                        data += chunk
                        if b"\n" in data:
                            break
                except socket.timeout:
                    pass

                msg = data.decode("utf-8", errors="ignore").strip()
                if not msg:
                    conn.sendall(b"ERR comando vacio\n")

                    continue

                # Acepta: "N" o "A 90" o "S 90"
                parts = msg.split()
                print(f"[TCP] Recibido: '{msg}' Partes: {parts}")
                if len(parts) == 1:
                    cmd = f"A"
                else:
                    cmd = f"{parts[0].upper()} {parts[-2]}"
                    
                try:
                    with _lock:
                        resp = send_to_arduino(ser, cmd)
                    conn.sendall((resp + "\n").encode("utf-8"))
                    log(f"Usuario: {parts[-1]} - Comando: '{cmd.replace(parts[-1], "")}' - Respuesta: '{resp}'")
                except Exception as e:
                    conn.sendall((f"ERR {e}\n").encode("utf-8"))
                    log(f"Usuario: {parts[-1]} - Comando: '{cmd}' - Error: {e}")

    try:
        ser.close()
        log("Puerto serial cerrado")
    except Exception:
        log("Error cerrando el puerto serial")
        pass
    
    print("Cerrado limpio.")

if __name__ == "__main__":
    main()

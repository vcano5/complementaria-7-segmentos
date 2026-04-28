from flask import Flask, render_template, request, jsonify
import socket

TCP_HOST = "127.0.0.1"
TCP_PORT = 5001

app = Flask(__name__, template_folder="templates")

def send_cmd(cmd: str) -> str:
    with socket.create_connection((TCP_HOST, TCP_PORT), timeout=3) as s:
        s.sendall((cmd.strip() + "\n").encode("UTF-8"))
        data = b""
        while b"\n" not in data:
            chunk = s.recv(1024)
            if not chunk:
                break
            data += chunk
        return data.decode("utf-8", errors="ignore").strip()
    
@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/apagar")
def handle_btn_num():
    ledn = request.args.get("n")
    send_cmd(f"N {ledn}")
    return jsonify({
        "status": "OK"
    }) 


@app.get("/api/btn")
def handle_btn_apagar():
    send_cmd("A")
    return jsonify({
        "status": "OK"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pywebpush import webpush, WebPushException

app = Flask(__name__)

VAPID_PUBLIC_KEY = "BNLvSpDWkI7hiEahzr8nw7-R2osnC4zG6fDzvB0giJCKo9rjAH6fxXEaWAjuxvh7kXImJTurfsx9zy8ddB6dUHM"
VAPID_PRIVATE_KEY = "R5DAsKCkqwbwEvpfJZ8-ZWEYA-nKgDcLVyXNVJN-tmk"

users = {}  # {username: {"subscription": ...}}
admin_password = "admin123"
replies = []  # {"user": username, "reply": mensagem}

@app.route("/")
def index():
    return render_template("index.html", vapid_public_key=VAPID_PUBLIC_KEY)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if password == admin_password:
            return redirect(url_for("admin"))
        if username:
            return redirect(url_for("index") + f"?username={username}")
    return render_template("login.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    return render_template("admin.html", users=users, replies=replies)

@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()
    username = data.get("username")
    subscription = data.get("subscription")
    if username and subscription:
        users[username] = {"subscription": subscription}
        print("Subscription registrada:", subscription)
    return jsonify({"success": True})

@app.route("/send_notification", methods=["POST"])
def send_notification():
    data = request.get_json()
    message = data.get("message")
    targets = data.get("targets")
    for user in targets:
        sub = users.get(user, {}).get("subscription")
        if sub:
            try:
                webpush(
                    subscription_info=sub,
                    data=message,
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": "mailto:you@example.com"},
                )
            except WebPushException as e:
                print(f"Erro enviando notificação para {user}: {str(e)}")
    return jsonify({"success": True})

@app.route("/responder")
def responder():
    return render_template("responder.html")

@app.route("/receive_reply", methods=["POST"])
def receive_reply():
    data = request.get_json()
    reply = data.get("reply")
    username = data.get("username")
    replies.append({"user": username, "reply": reply})
    print(f"{username} respondeu: {reply}")
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
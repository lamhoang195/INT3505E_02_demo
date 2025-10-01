from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from ..app import DATA_PATHS
from ..storage import read_json, write_json


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form if request.form else request.get_json(silent=True) or {}
        username = data.get("username", "").strip()
        password = data.get("password", "")
        users = read_json(DATA_PATHS["USERS_PATH"], {"users": []})
        user = next((u for u in users.get("users", []) if u.get("username") == username), None)
        if user and check_password_hash(user.get("password_hash", ""), password):
            session["username"] = user["username"]
            session["role"] = user.get("role", "user")
            if request.is_json:
                return jsonify({"ok": True, "role": session["role"]})
            return redirect(url_for("admin.dashboard" if session["role"] == "admin" else "user.dashboard"))
        if request.is_json:
            return jsonify({"ok": False, "error": "Invalid credentials"}), 401
        return render_template("login.html", error="Sai tài khoản hoặc mật khẩu")
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form if request.form else request.get_json(silent=True) or {}
        username = data.get("username", "").strip()
        password = data.get("password", "")
        role = data.get("role", "user")
        if not username or not password:
            return render_template("register.html", error="Vui lòng nhập đủ thông tin")
        users = read_json(DATA_PATHS["USERS_PATH"], {"users": []})
        if any(u.get("username") == username for u in users.get("users", [])):
            return render_template("register.html", error="Tên đăng nhập đã tồn tại")
        users["users"].append({
            "username": username,
            "password_hash": generate_password_hash(password),
            "role": role if role in ("user", "admin") else "user",
        })
        write_json(DATA_PATHS["USERS_PATH"], users)
        return redirect(url_for("auth.login"))
    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))



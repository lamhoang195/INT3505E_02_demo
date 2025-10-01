from flask import Flask, render_template, redirect, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps
from .storage import read_json, write_json, ensure_parent_dir


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_PATH = os.path.join(DATA_DIR, "users.json")
BOOKS_PATH = os.path.join(DATA_DIR, "books.json")
BORROWS_PATH = os.path.join(DATA_DIR, "borrows.json")


def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(BASE_DIR), "frontend", "templates"))
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

    # Seed data files if missing
    ensure_parent_dir(USERS_PATH)
    read_json(USERS_PATH, {"users": []})
    read_json(BOOKS_PATH, {"books": []})
    read_json(BORROWS_PATH, {"borrows": []})

    # Ensure an initial admin exists
    users = read_json(USERS_PATH, {"users": []})
    if not any(u.get("role") == "admin" for u in users.get("users", [])):
        users["users"].append({
            "username": "admin",
            "password_hash": generate_password_hash("admin123"),
            "role": "admin"
        })
        write_json(USERS_PATH, users)

    from .auth.routes import auth_bp
    from .admin.routes import admin_bp
    from .user.routes import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(user_bp, url_prefix="/user")

    @app.route("/")
    def index():
        if session.get("role") == "admin":
            return redirect(url_for("admin.dashboard"))
        if session.get("role") == "user":
            return redirect(url_for("user.dashboard"))
        return redirect(url_for("auth.login"))

    return app


def login_required(role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not session.get("username"):
                return redirect(url_for("auth.login"))
            if role and session.get("role") != role:
                return redirect(url_for("auth.login"))
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# Expose paths for other modules
DATA_PATHS = {
    "USERS_PATH": USERS_PATH,
    "BOOKS_PATH": BOOKS_PATH,
    "BORROWS_PATH": BORROWS_PATH,
}



from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from ..app import login_required, DATA_PATHS
from ..storage import read_json, write_json


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required(role="admin")
def dashboard():
    books = read_json(DATA_PATHS["BOOKS_PATH"], {"books": []}).get("books", [])
    borrows = read_json(DATA_PATHS["BORROWS_PATH"], {"borrows": []}).get("borrows", [])
    return render_template("admin.html", books=books, borrows=borrows)


@admin_bp.route("/books", methods=["POST"])  # create
@login_required(role="admin")
def create_book():
    data = request.get_json(force=True)
    title = data.get("title", "").strip()
    author = data.get("author", "").strip()
    books_doc = read_json(DATA_PATHS["BOOKS_PATH"], {"books": []})
    books = books_doc.get("books", [])
    new_id = (max((b.get("id", 0) for b in books), default=0) + 1)
    books.append({"id": new_id, "title": title, "author": author, "available": True})
    write_json(DATA_PATHS["BOOKS_PATH"], {"books": books})
    return jsonify({"ok": True, "id": new_id})


@admin_bp.route("/books/<int:book_id>", methods=["PUT"])  # update
@login_required(role="admin")
def update_book(book_id: int):
    data = request.get_json(force=True)
    books_doc = read_json(DATA_PATHS["BOOKS_PATH"], {"books": []})
    books = books_doc.get("books", [])
    for b in books:
        if b.get("id") == book_id:
            b.update({k: v for k, v in data.items() if k in ("title", "author", "available")})
            write_json(DATA_PATHS["BOOKS_PATH"], {"books": books})
            return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "Not found"}), 404


@admin_bp.route("/books/<int:book_id>", methods=["DELETE"])  # delete
@login_required(role="admin")
def delete_book(book_id: int):
    books_doc = read_json(DATA_PATHS["BOOKS_PATH"], {"books": []})
    books = [b for b in books_doc.get("books", []) if b.get("id") != book_id]
    write_json(DATA_PATHS["BOOKS_PATH"], {"books": books})
    # Also remove borrows for this book
    borrows_doc = read_json(DATA_PATHS["BORROWS_PATH"], {"borrows": []})
    borrows_doc["borrows"] = [br for br in borrows_doc.get("borrows", []) if br.get("book_id") != book_id]
    write_json(DATA_PATHS["BORROWS_PATH"], borrows_doc)
    return jsonify({"ok": True})


@admin_bp.route("/borrows", methods=["GET"])  # list borrows
@login_required(role="admin")
def list_borrows():
    return jsonify(read_json(DATA_PATHS["BORROWS_PATH"], {"borrows": []}))


@admin_bp.route("/borrows/<int:borrow_id>", methods=["DELETE"])  # remove record
@login_required(role="admin")
def delete_borrow(borrow_id: int):
    borrows_doc = read_json(DATA_PATHS["BORROWS_PATH"], {"borrows": []})
    borrows = borrows_doc.get("borrows", [])
    target = next((br for br in borrows if br.get("id") == borrow_id), None)
    if not target:
        return jsonify({"ok": False, "error": "Not found"}), 404

    # Mark related book as available again
    books_doc = read_json(DATA_PATHS["BOOKS_PATH"], {"books": []})
    books = books_doc.get("books", [])
    for b in books:
        if b.get("id") == target.get("book_id"):
            b["available"] = True
            break
    write_json(DATA_PATHS["BOOKS_PATH"], {"books": books})

    # Remove borrow record
    borrows = [br for br in borrows if br.get("id") != borrow_id]
    write_json(DATA_PATHS["BORROWS_PATH"], {"borrows": borrows})
    return jsonify({"ok": True})



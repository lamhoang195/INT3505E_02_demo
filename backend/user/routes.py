from flask import Blueprint, render_template, request, jsonify, session
from ..app import login_required, DATA_PATHS
from ..storage import read_json, write_json


user_bp = Blueprint("user", __name__)


@user_bp.route("/")
@login_required(role="user")
def dashboard():
    books = read_json(DATA_PATHS["BOOKS_PATH"], {"books": []}).get("books", [])
    borrows = read_json(DATA_PATHS["BORROWS_PATH"], {"borrows": []}).get("borrows", [])
    my = [br for br in borrows if br.get("username") == session.get("username")]
    return render_template("user.html", books=books, my_borrows=my)


@user_bp.route("/books", methods=["GET"])  # list
@login_required(role="user")
def list_books():
    return jsonify(read_json(DATA_PATHS["BOOKS_PATH"], {"books": []}))


@user_bp.route("/borrow/<int:book_id>", methods=["POST"])  # borrow
@login_required(role="user")
def borrow_book(book_id: int):
    books_doc = read_json(DATA_PATHS["BOOKS_PATH"], {"books": []})
    books = books_doc.get("books", [])
    book = next((b for b in books if b.get("id") == book_id), None)
    if not book or not book.get("available", True):
        return jsonify({"ok": False, "error": "Book unavailable"}), 400
    borrows_doc = read_json(DATA_PATHS["BORROWS_PATH"], {"borrows": []})
    borrows = borrows_doc.get("borrows", [])
    new_id = (max((br.get("id", 0) for br in borrows), default=0) + 1)
    borrows.append({"id": new_id, "book_id": book_id, "username": session.get("username")})
    write_json(DATA_PATHS["BORROWS_PATH"], {"borrows": borrows})
    # mark book unavailable
    for b in books:
        if b.get("id") == book_id:
            b["available"] = False
            break
    write_json(DATA_PATHS["BOOKS_PATH"], {"books": books})
    return jsonify({"ok": True, "borrow_id": new_id})


@user_bp.route("/return/<int:borrow_id>", methods=["POST"])  # return
@login_required(role="user")
def return_book(borrow_id: int):
    borrows_doc = read_json(DATA_PATHS["BORROWS_PATH"], {"borrows": []})
    borrows = borrows_doc.get("borrows", [])
    borrow = next((br for br in borrows if br.get("id") == borrow_id and br.get("username") == session.get("username")), None)
    if not borrow:
        return jsonify({"ok": False, "error": "Borrow not found"}), 404
    borrows = [br for br in borrows if br.get("id") != borrow_id]
    write_json(DATA_PATHS["BORROWS_PATH"], {"borrows": borrows})
    # mark book available
    books_doc = read_json(DATA_PATHS["BOOKS_PATH"], {"books": []})
    books = books_doc.get("books", [])
    for b in books:
        if b.get("id") == borrow.get("book_id"):
            b["available"] = True
            break
    write_json(DATA_PATHS["BOOKS_PATH"], {"books": books})
    return jsonify({"ok": True})



from flask import Flask
from .extensions import db, migrate
from .models import show_author_books, check_author_books_status, check_book_status, borrow_book, return_book


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    from .models import Book, Author, Loan

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'Book': Book,
            'Author': Author,
            'Loan': Loan,
            'check_book_status': check_book_status,
            'check_author_books_status' : check_author_books_status,
            'show_author_books': show_author_books,
            'borrow_book': borrow_book,
            'return_book': return_book
        }

    return app
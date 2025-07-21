from .extensions import db
from datetime import datetime

book_author = db.Table('book_author',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'), primary_key=True)
)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    books = db.relationship('Book', secondary=book_author, back_populates='authors')

    def __repr__(self):
        return f"Autor: '{self.name}'>"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    authors = db.relationship('Author', secondary=book_author, back_populates='books')
    is_available = db.Column(db.Boolean, default=True)
    loans = db.relationship('Loan', back_populates='book', cascade='all, delete-orphan')

    def __repr__(self):
        return f"Książka: '{self.title}'"

    @property
    def is_on_shelf(self):
        return not any(loan.return_date is None for loan in self.loans)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    borrower = db.Column(db.String(128), nullable=False)
    loan_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    book = db.relationship('Book', back_populates='loans')

def show_author_books(author_name):
    author = Author.query.filter_by(name=author_name).first()
    if author:
        print(f"Autor: {author.name}")
        if author.books:
            for book in author.books:
                print(f" - {book.title}")
        else:
            print("Autor nie ma przypisanych książek.")
    else:
        print("Nie znaleziono autora.")

def check_author_books_status(author_name):
    author = Author.query.filter_by(name=author_name).first()
    if not author:
        print(f"Nie znaleziono autora: {author_name}")
        return
    if not author.books:
        print(f"Autor {author_name} nie ma przypisanych książek.")
        return
    for book in author.books:
        status = "dostępna" if book.is_on_shelf else "wypożyczona"
        print(f"Książka: {book.title} - Status: {status}")

def check_book_status(title):
    book = Book.query.filter_by(title=title).first()
    if not book:
        print(f"Nie znaleziono książki o tytule: {title}")
        return
    status = "dostępna na półce" if book.is_on_shelf else "wypożyczona"
    print(f"Książka '{book.title}' jest {status}.")

def borrow_book(title, borrower):
    book = Book.query.filter_by(title=title).first()
    if not book:
        print(f"Nie znaleziono książki o tytule: {title}")
        return
    if not book.is_on_shelf:
        print(f"Książka '{title}' jest już wypożyczona")
        return
    loan = Loan(borrower=borrower, book=book)
    db.session.add(loan)
    db.session.commit()
    print(f"Wypożyczono książkę '{title}' dla {borrower}")


from datetime import datetime


def return_book(title, borrower):
    book = Book.query.filter_by(title=title).first()
    if not book:
        print(f"Nie znaleziono książki o tytule: {title}")
        return

    loan = Loan.query.filter_by(book=book, borrower=borrower, return_date=None).first()
    if not loan:
        print(f"Nie znaleziono aktywnego wypożyczenia dla '{title}' przez {borrower}")
        return

    loan.return_date = datetime.utcnow()
    db.session.commit()
    print(f"Książka '{title}' została zwrócona przez {borrower}")


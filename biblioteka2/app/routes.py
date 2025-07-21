from flask import request, jsonify
from app import db
from app.models import Book, Author, Loan
from app import create_app

app = create_app()


@app.route('/')
def index():
    return jsonify({'message': 'Domowa Biblioteka API'})


@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    title = data.get('title')
    authors_data = data.get('authors', [])

    if not title:
        return jsonify({'error': 'Missing title'}), 400

    authors = []
    for author_name in authors_data:
        author = Author.query.filter_by(name=author_name).first()
        if not author:
            author = Author(name=author_name)
            db.session.add(author)
        authors.append(author)

    book = Book(title=title, authors=authors)
    db.session.add(book)
    db.session.commit()

    return jsonify({'message': 'Book added', 'book_id': book.id})


@app.route('/loans', methods=['POST'])
def loan_book():
    data = request.json
    book_id = data.get('book_id')
    borrower = data.get('borrower')

    book = Book.query.get_or_404(book_id)

    if not book.is_available:
        return jsonify({'error': 'Book is already loaned'}), 400

    loan = Loan(borrower=borrower, book=book)
    book.is_available = False
    db.session.add(loan)
    db.session.commit()

    return jsonify({'message': 'Book loaned', 'loan_id': loan.id})


@app.route('/returns/<int:loan_id>', methods=['POST'])
def return_book(loan_id):
    loan = Loan.query.get_or_404(loan_id)

    if loan.return_date:
        return jsonify({'error': 'Book already returned'}), 400

    loan.return_date = db.func.now()
    loan.book.is_available = True
    db.session.commit()

    return jsonify({'message': 'Book returned'})

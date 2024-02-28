from flask import Flask,render_template
from book_recommender import recommend


# Recommend function returns 5 books when the book-title is right otherwise it returns false

app = Flask(__name__)

@app.route('/')
def hello_world():
    books,book_image_url = recommend(" The Two Towers (The Lord of the Rings, Part 2)")
    if books:
     
        print(books)
        return render_template('index.html',book = books)
    else:
        return render_template('index.html',book = "Wrong Book Input")

if __name__ == '__main__':
    app.run(debug=True)


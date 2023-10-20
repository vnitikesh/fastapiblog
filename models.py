from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from pydantic import EmailStr
from sqlalchemy.orm import relationship




class Blog(Base):
    __tablename__ = 'blogs'

    id = Column(Integer, primary_key = True, index = True)
    title = Column(String)
    body = Column(String)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True, index = True, nullable = False)
    email = Column(String, nullable = False, unique = True)
    password = Column(String, nullable = False)
    first_name = Column(String, nullable = False)
    last_name = Column(String, nullable = False)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key = True, index = True, nullable = False)
    user = Column(Integer, ForeignKey('users.id', ondelete = "CASCADE"))
    title = Column(String)
    content = Column(String)

    def as_json(self):
        return dict(
            id = self.id,
            posted_by = f'{self.user.first_name} + " " + {self.user.last_name}',
            post = self.post
        )

book_authors = Table(  #Imperative Style
    "book_authors", Base.metadata,
    Column('book_id', ForeignKey('books.id'), primary_key = True),
    Column('author_id', ForeignKey('authors.id'),primary_key = True)
)

# class BookAuthor(Base):
#     __tablename__ = 'book_authors'

#     id = Column(Integer, primary_key = True)
#     book_id = Column(Integer, ForeignKey('books.id', ondelete= "CASCADE"))
#     author_id = Column(Integer, ForeignKey('authors.id', on_delete = "CASCADE"))

class Book(Base): #Delcarative Style
    __tablename__ = 'books'

    id = Column(Integer, primary_key = True)
    title = Column(String)
    authors = relationship('Author', secondary = "book_authors", back_populates = 'books')


class Author(Base): #Declarative Style
    __tablename__ = 'authors'

    id = Column(Integer, primary_key = True)
    name = Column(String)
    books = relationship('Book', secondary = 'book_authors', back_populates = 'authors')

class Assistant(Base):
    __tablename__ = 'assistants'
    id = Column(Integer, primary_key = True)
    name = Column(String)
    authors = Column(ForeignKey('authors.id'))




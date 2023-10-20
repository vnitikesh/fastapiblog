from fastapi import FastAPI, Depends, status, Response, HTTPException, Request
from schemas import Blog
from database import engine, SessionLocal
import models
from sqlalchemy.orm import Session
import schemas
from typing import List, Dict
from fastapi.security import OAuth2PasswordBearer
import time
import jwt

from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


app = FastAPI()

models.Base.metadata.create_all(engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl= "token")

SECRET_KEY = '13f4e829aaea762d91f9d4f9ca68be93d4c1eb6d3d993fc03e161dc866e0da93'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print("error in db:- " + str(e))
    finally:
        db.close()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hasher():
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)





def signJWT(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + ACCESS_TOKEN_EXPIRE_MINUTES*60 
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm= ALGORITHM)
    return {
        "access_token": token
    }


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded_token["expires"] >= time.time():
            return decoded_token
        else:
            None
    except:
        return {}



class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error= auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "Invalid authentication scheme")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "Invalid Token or Expired Token")
            return credentials.credentials
        else:
            raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "Invalid authorization code")
        pass

    def verify_jwt(self, jwtoken:str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decode_jwt(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid


# @app.post("/posts", dependencies= [Depends(JWTBearer())], tags= ['Posts'])
# async def create_post(post: schemas.PostSchema) -> dict:
#     new_post = models.Post(
#         title = post.title,
#         content = post.content,
#         user = fastapi_users
#     )
#     pass


@app.post('/user/signup', tags= ["User"])
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(
        first_name = user.first_name,
        last_name = user.last_name,
        email= user.email,
        password = Hasher.get_password_hash(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return signJWT(user.email)

@app.post("/user/login", tags= ["User"])
async def user_login(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.email).first()
    if not user:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Incorrect Email")
    
    hashed_password = user.password
    if not Hasher.verify_password(form_data.password, hashed_password):
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Incorrect Password")
    return signJWT(user.email)

@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}

def fake_decoded_token(token):
    user = schemas.User(
        username= token + "fakedecoded",
        email= 'nk@example.com',
        full_name= 'nk'
    )
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    current_user = fake_decoded_token(token)
    return current_user
    pass

@app.get('/users/me')
async def read_users_me(current_user: str = Depends(get_current_user)):
    return current_user

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     except Exception as e:
#         print(e)
#     finally:
#         db.close()
    


@app.post('/blog', status_code= status.HTTP_201_CREATED)
def blog(request: Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title = request.title, body = request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.get('/blog', response_model= List[schemas.ShowBlog])
def get_all_blogs(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs


@app.get('/blog/{id}', response_model= schemas.ShowBlog)
def show(id, response:Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail = f"Data with id = {id} does not exist")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"data":f"Data with id = {id} doest not exist"}
    return blog

@app.delete('/blog/{id}', status_code= status.HTTP_404_NOT_FOUND)
def destroy(id, response:Response, db: Session = Depends(get_db)):
    db.query(models.Blog).filter(models.Blog.id == id).delete(synchronize_session= False)
    db.commit()
    return 'Deleted'

@app.put('/blog/{id}', status_code = status.HTTP_202_ACCEPTED)
def update_blog(id, request: Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f'Blog with id = {id} does not exist')
    blog.update(request.dict())
    db.commit()
    return 'Updated Successfully' 



@app.post('/insert_data', status_code= status.HTTP_201_CREATED)
def insert_data(db: Session = Depends(get_db)) -> str:
    book1 = models.Book(title = "Dead People who would be influencers today")
    book2 = models.Book(title = "How to make friends in your 30s")

  

    author1 = models.Author(name = "Blu Renolds")
    author2 = models.Author(name = 'Chip Egan')
    author3 = models.Author(name = 'Alyssa Wyatt')

    

    book1.authors = [author1, author2]
    book2.authors = [author1, author3]

    db.add_all([book1, book2, author1, author2, author3])
    db.commit()

    assist1 = models.Assistant(name= 'abdul', authors = author1.id)
    assist2 = models.Assistant(name = 'Tim', authors = author2.id)
    assist3 = models.Assistant(name = 'Victor', authors = author1.id)
    assist4 = models.Assistant(name = 'Daniel', authors = author2.id)

    db.add_all([assist1, assist2, assist3, assist4])
    db.commit()

    return 'Data inserted successfully'


@app.get('/book/{id}', status_code= status.HTTP_200_OK)
def get_book(id, db: Session = Depends(get_db)):

    # book = db.query(models.Book).options(joinedload(models.Book.authors)).filter(models.Book.id == id).first()
    book = db.query(models.Book).filter(models.Book.id == id).first()
    msg = {
        'name': book.title,
        'author':[author.name for author in book.authors]
    }
    return msg

from sqlalchemy.orm import joinedload

@app.get('/books', status_code= status.HTTP_200_OK, response_model= List[schemas.BookSchema])
def book(db: Session = Depends(get_db)): 
    book = db.query(models.Book).options(joinedload(models.Book.authors)).all()
    return book



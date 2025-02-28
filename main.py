from fastapi import FastAPI, status, Response
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from icecream import ic

# CRUD - Create, Read, Update, Delete

COUNTER = 0 # Счетчик, имитирующий присвоение id в базе данных

app = FastAPI(
    title="Book Library App",
    description="Учебное приложение для MTS SAD",
    version="0.0.1",
    default_response_class=ORJSONResponse,
    responses={404: {"description": "Not found!"}},
)

fake_storage = {}

class BaseBook(BaseModel):
    title: str
    author: str
    year: int

class IncomingBook(BaseBook):
    pages: int = Field(default=150, alias="count_pages")
    
    @field_validator("year")
    @staticmethod
    def validate_year(val: int):
        if val < 2020:
            raise PydanticCustomError("validation error", "Year is too old!")
        
        return val

class ReturnedBook(BaseBook):
    id: int
    pages: int
    
class ReturnedAllbooks(BaseModel):
    books: list[ReturnedBook]

# End point (ручки) - адрес или место,
# куда направляется запрос,
# чтобы получить необходимую информацию
# или действие от системы.
# get - принимает путь на нашем сайте

@app.get("/", include_in_schema=False)
async def main():
    return "Hello World!"

# get(дай) и post (получи/сохрани) - методы REST архитектуры (сервис не запоминает взаимодействия между сервером и клиентом)
# ручка сохренения книги
# @app.post("/books/", status_code=status.HTTP_201_CREATED)
@app.post("/books/", response_model=ReturnedBook)
async def create_book(book: IncomingBook):
    global COUNTER
    new_book = {
        "id": COUNTER,
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "pages": book.pages,
    }
    
    fake_storage[COUNTER] = new_book
    COUNTER += 1
    
    return ORJSONResponse({"book": new_book}, status_code=status.HTTP_201_CREATED)

# хотим получить весь список книг, которые накидали
@app.get("/books/", response_model=ReturnedAllbooks)
async def get_all_books():
    # Хотим в формате:
    # books: [{"id": 1, "title": "fkjdj",  ..., "year": 2000}, {...}]
    # ключи в словаре - COUNTERы
    books = list(fake_storage.values())
    return {"books": books}

@app.get("/books/{book_id}", response_model=ReturnedBook)
async def get_book(book_id: int):
    book = fake_storage.get(book_id)
    if book is not None:
        return book
    
    return Response(status_code=status.HTTP_404_NOT_FOUND)

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    deleted_book = fake_storage.pop(book_id, None)
    ic(deleted_book)
    # return Response(status_code=status.HTTP_204_NO_CONTENT)

# put = переписывает полностью
# patch = обновляет только те поля, которые в него пришли

@app.put("/books/{book_id}", response_model=ReturnedBook)
async def update_book(book_id: int, new_book_data: ReturnedBook):
    if _ := fake_storage.get(book_id, None):
        new_book = {
            "id": book_id,
            "title": new_book_data.title,
            "author": new_book_data.author,
            "year": new_book_data.year,
            "pages": new_book_data.pages,
        }
        
        fake_storage[book_id] = new_book
        
    return fake_storage[book_id]
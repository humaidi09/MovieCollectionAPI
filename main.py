from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import models
from models import Movies, MovieCreate, MovieUpdate
from typing import Annotated
from database import engine, SessionLocal

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/movies")
def get_movies(db: Annotated[Session, Depends(get_db)]):
    return db.query(Movies).all()


@app.get("/movies/sort")
def sort_movies(
    db: Annotated[Session, Depends(get_db)],
    sort_by: str = Query(default="rating"),
    order: str = Query(default="desc")
):

    if sort_by not in ["duration", "rating"]:
        raise HTTPException(
            status_code=422,
            detail="sort_by must be duration or rating"
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=422,
            detail="order must be asc or desc"
        )

    if sort_by == "duration":
        col = Movies.duration
    else:
        col = Movies.rating

    if order == "asc":
        mov = db.query(Movies).order_by(col.asc()).all()
    else:
        mov = db.query(Movies).order_by(col.desc()).all()

    return mov


@app.get("/movies/{movie_id}")
def get_movie(
    movie_id: int,
    db: Annotated[Session, Depends(get_db)]
):

    mov = db.query(Movies).filter(
        Movies.movie_id == movie_id
    ).first()

    if mov is None:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    return mov


@app.post("/create_movies", status_code=201)
def create_movie(
    movie: MovieCreate,
    db: Annotated[Session, Depends(get_db)]
):

    old = db.query(Movies).filter(
        Movies.movie_id == movie.movie_id
    ).first()

    if old:
        raise HTTPException(
            status_code=400,
            detail="Movie with this movie_id already exists"
        )

    new = Movies(
        movie_id=movie.movie_id,
        title=movie.title,
        director=movie.director,
        genre=movie.genre,
        duration=movie.duration,
        rating=movie.rating
    )

    db.add(new)
    db.commit()
    db.refresh(new)

    return new


@app.put("/movies/{movie_id}")
def update_movie(
    movie_id: int,
    movie: MovieUpdate,
    db: Annotated[Session, Depends(get_db)]
):

    old = db.query(Movies).filter(
        Movies.movie_id == movie_id
    ).first()

    if old is None:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    old.title = movie.title
    old.director = movie.director
    old.genre = movie.genre
    old.duration = movie.duration
    old.rating = movie.rating

    db.commit()
    db.refresh(old)

    return old


@app.delete("/movies/{movie_id}")
def delete_movie(
    movie_id: int,
    db: Annotated[Session, Depends(get_db)]
):

    mov = db.query(Movies).filter(
        Movies.movie_id == movie_id
    ).first()

    if mov is None:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    db.delete(mov)
    db.commit()

    return {"message": "Movie deleted successfully"}
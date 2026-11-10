from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from decimal import Decimal

from database import engine


app = FastAPI(
    title="Smart Business CRUD API",
    description="Product Management System using FastAPI and TiDB Cloud",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# PRODUCT SCHEMA
# -----------------------------

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    category: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(gt=0)
    quantity: int = Field(ge=0)


class ProductUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    category: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(gt=0)
    quantity: int = Field(ge=0)


# -----------------------------
# HOME ROUTE
# -----------------------------

@app.get("/")
def root():
    return {
        "message": "Smart Business CRUD API is running"
    }


# -----------------------------
# HEALTH CHECK
# -----------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# -----------------------------
# DATABASE TEST
# -----------------------------

@app.get("/db-test")
def database_test():

    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT DATABASE()")
            )

            database_name = result.scalar()

        return {
            "status": "success",
            "message": "TiDB Cloud connected successfully!",
            "database": database_name
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# -----------------------------
# CREATE PRODUCT
# -----------------------------

@app.post("/products", status_code=201)
def create_product(product: ProductCreate):

    with engine.begin() as connection:

        result = connection.execute(
            text("""
                INSERT INTO products
                (name, category, price, quantity)
                VALUES
                (:name, :category, :price, :quantity)
            """),
            product.model_dump()
        )

        product_id = result.lastrowid

        new_product = connection.execute(
            text("""
                SELECT *
                FROM products
                WHERE id = :product_id
            """),
            {"product_id": product_id}
        ).mappings().first()

    return {
        "message": "Product created successfully",
        "product": dict(new_product)
    }


# -----------------------------
# READ ALL PRODUCTS
# -----------------------------

@app.get("/products")
def get_products():

    with engine.connect() as connection:

        result = connection.execute(
            text("""
                SELECT *
                FROM products
                ORDER BY id DESC
            """)
        )

        products = result.mappings().all()

    return {
        "total": len(products),
        "products": [dict(product) for product in products]
    }


# -----------------------------
# READ SINGLE PRODUCT
# -----------------------------

@app.get("/products/{product_id}")
def get_product(product_id: int):

    with engine.connect() as connection:

        product = connection.execute(
            text("""
                SELECT *
                FROM products
                WHERE id = :product_id
            """),
            {"product_id": product_id}
        ).mappings().first()

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return dict(product)


# -----------------------------
# UPDATE PRODUCT
# -----------------------------

@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    product: ProductUpdate
):

    with engine.begin() as connection:

        result = connection.execute(
            text("""
                UPDATE products
                SET
                    name = :name,
                    category = :category,
                    price = :price,
                    quantity = :quantity
                WHERE id = :product_id
            """),
            {
                **product.model_dump(),
                "product_id": product_id
            }
        )

        if result.rowcount == 0:

            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        updated_product = connection.execute(
            text("""
                SELECT *
                FROM products
                WHERE id = :product_id
            """),
            {"product_id": product_id}
        ).mappings().first()

    return {
        "message": "Product updated successfully",
        "product": dict(updated_product)
    }


# -----------------------------
# DELETE PRODUCT
# -----------------------------

@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    with engine.begin() as connection:

        result = connection.execute(
            text("""
                DELETE FROM products
                WHERE id = :product_id
            """),
            {"product_id": product_id}
        )

        if result.rowcount == 0:

            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

    return {
        "message": "Product deleted successfully",
        "product_id": product_id
    }
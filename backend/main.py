import os
from decimal import Decimal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import engine


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="Smart Business CRUD API",
    description="Product Management System using FastAPI and TiDB Cloud",
    version="1.0.0"
)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

allowed_origins = [
    "http://localhost:5173",
    "https://smart-business-crud-frontend.vercel.app"
]

frontend_url = os.getenv("FRONTEND_URL")

if frontend_url:
    frontend_url = frontend_url.rstrip("/")

    if frontend_url not in allowed_origins:
        allowed_origins.append(frontend_url)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# PRODUCT SCHEMAS
# --------------------------------------------------

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


# --------------------------------------------------
# HOME ROUTE
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Smart Business CRUD API is running",
        "status": "success"
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "message": "API is running successfully"
    }


# --------------------------------------------------
# DATABASE TEST
# --------------------------------------------------

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

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed. Check database configuration."
        )


# --------------------------------------------------
# CREATE PRODUCT
# --------------------------------------------------

@app.post("/products", status_code=201)
def create_product(product: ProductCreate):

    try:
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

        if not new_product:
            raise HTTPException(
                status_code=500,
                detail="Product created but could not be retrieved"
            )

        return {
            "message": "Product created successfully",
            "product": dict(new_product)
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Failed to create product"
        )


# --------------------------------------------------
# READ ALL PRODUCTS
# --------------------------------------------------

@app.get("/products")
def get_products():

    try:
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
            "products": [
                dict(product) for product in products
            ]
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve products"
        )


# --------------------------------------------------
# READ SINGLE PRODUCT
# --------------------------------------------------

@app.get("/products/{product_id}")
def get_product(product_id: int):

    try:
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

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve product"
        )


# --------------------------------------------------
# UPDATE PRODUCT
# --------------------------------------------------

@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    product: ProductUpdate
):

    try:
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

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Failed to update product"
        )


# --------------------------------------------------
# DELETE PRODUCT
# --------------------------------------------------

@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    try:
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

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete product"
        )
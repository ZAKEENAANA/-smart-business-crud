import { useEffect, useState } from "react";
import "./App.css";

interface Product {
  id: number;
  name: string;
  category: string;
  price: number;
  quantity: number;
  created_at?: string;
}

const API_URL = "https://smart-business-crud-api.vercel.app";

function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    name: "",
    category: "",
    price: "",
    quantity: "",
  });

  // GET PRODUCTS
  const fetchProducts = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/products`);

      if (!response.ok) {
        throw new Error("Unable to load products");
      }

      const data = await response.json();
      setProducts(data.products);
    } catch {
      setError("Cannot connect to backend. Check whether FastAPI is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  // FORM INPUT
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  // CREATE / UPDATE
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const productData = {
      name: form.name.trim(),
      category: form.category.trim(),
      price: Number(form.price),
      quantity: Number(form.quantity),
    };

    if (
      !productData.name ||
      !productData.category ||
      !Number.isFinite(productData.price) ||
      productData.price <= 0 ||
      !Number.isInteger(productData.quantity) ||
      productData.quantity < 0
    ) {
      alert("Please enter valid product details.");
      return;
    }

    try {
      const url = editingId
        ? `${API_URL}/products/${editingId}`
        : `${API_URL}/products`;

      const response = await fetch(url, {
        method: editingId ? "PUT" : "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(productData),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Operation failed");
      }

      alert(editingId ? "Product updated!" : "Product added!");

      resetForm();
      fetchProducts();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Something went wrong");
    }
  };

  // EDIT PRODUCT
  const handleEdit = (product: Product) => {
    setEditingId(product.id);

    setForm({
      name: product.name,
      category: product.category,
      price: String(product.price),
      quantity: String(product.quantity),
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // DELETE PRODUCT
  const handleDelete = async (id: number) => {
    if (!window.confirm("Are you sure you want to delete this product?")) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/products/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Unable to delete product");
      }

      alert("Product deleted successfully!");
      fetchProducts();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Delete failed");
    }
  };

  // RESET FORM
  const resetForm = () => {
    setEditingId(null);

    setForm({
      name: "",
      category: "",
      price: "",
      quantity: "",
    });
  };

  const filteredProducts = products.filter((product) =>
    `${product.name} ${product.category}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  const totalValue = products.reduce(
    (total, product) => total + product.price * product.quantity,
    0
  );

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>Smart Business</h1>
          <p>Product Management System</p>
        </div>

        <span className="status">● Backend Connected</span>
      </header>

      <main className="container">
        <section className="welcome">
          <h2>Dashboard</h2>
          <p>Manage your business products in one place.</p>
        </section>

        <section className="stats">
          <div className="stat-card">
            <span>Total Products</span>
            <h2>{products.length}</h2>
          </div>

          <div className="stat-card">
            <span>Total Stock Quantity</span>
            <h2>
              {products.reduce(
                (total, product) => total + product.quantity,
                0
              )}
            </h2>
          </div>

          <div className="stat-card">
            <span>Estimated Stock Value</span>
            <h2>
              LKR {totalValue.toLocaleString("en-LK", {
                maximumFractionDigits: 2,
              })}
            </h2>
          </div>
        </section>

        <section className="content-grid">
          <div className="panel form-panel">
            <h3>{editingId ? "Update Product" : "Add New Product"}</h3>

            <form onSubmit={handleSubmit}>
              <label>Product Name</label>
              <input
                name="name"
                value={form.name}
                onChange={handleChange}
                placeholder="Enter product name"
                required
              />

              <label>Category</label>
              <input
                name="category"
                value={form.category}
                onChange={handleChange}
                placeholder="Enter category"
                required
              />

              <label>Price (LKR)</label>
              <input
                name="price"
                type="number"
                min="0.01"
                step="0.01"
                value={form.price}
                onChange={handleChange}
                placeholder="Enter price"
                required
              />

              <label>Quantity</label>
              <input
                name="quantity"
                type="number"
                min="0"
                step="1"
                value={form.quantity}
                onChange={handleChange}
                placeholder="Enter quantity"
                required
              />

              <button className="primary-btn" type="submit">
                {editingId ? "Update Product" : "Add Product"}
              </button>

              {editingId && (
                <button
                  className="cancel-btn"
                  type="button"
                  onClick={resetForm}
                >
                  Cancel
                </button>
              )}
            </form>
          </div>

          <div className="panel table-panel">
            <div className="table-heading">
              <div>
                <h3>Product Inventory</h3>
                <p>Manage your available products</p>
              </div>

              <input
                className="search"
                placeholder="Search products..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            {error && <p className="error">{error}</p>}

            {loading ? (
              <p className="empty">Loading products...</p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Product</th>
                      <th>Category</th>
                      <th>Price</th>
                      <th>Quantity</th>
                      <th>Actions</th>
                    </tr>
                  </thead>

                  <tbody>
                    {filteredProducts.map((product) => (
                      <tr key={product.id}>
                        <td>{product.id}</td>
                        <td>{product.name}</td>
                        <td>{product.category}</td>
                        <td>
                          LKR {Number(product.price).toLocaleString("en-LK")}
                        </td>
                        <td>{product.quantity}</td>
                        <td>
                          <div className="actions">
                            <button
                              className="edit-btn"
                              onClick={() => handleEdit(product)}
                            >
                              Edit
                            </button>

                            <button
                              className="delete-btn"
                              onClick={() => handleDelete(product.id)}
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}

                    {filteredProducts.length === 0 && (
                      <tr>
                        <td colSpan={6} className="empty">
                          No products found.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
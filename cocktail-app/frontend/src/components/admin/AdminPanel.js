import React, { useCallback, useEffect, useState } from 'react';
import { createCocktail, deleteCocktail, listCocktailsAdmin, updateCocktail, uploadCocktailImage } from '../../api/cocktails';
import { createServiceAddon, deleteServiceAddon, listServiceAddonsAdmin, updateServiceAddon } from '../../api/business';
import { listAllOrders, updateOrderStatus } from '../../api/orders';
import { getApiErrorMessage } from '../../api/http';

const emptyProduct = { name: '', description: '', category: 'Cócteles', price_cop: '', instructions: '', ingredientsText: '', image: '', is_available: true };
const emptyAddon = { name: '', description: '', price_cop: '' };
const orderStatuses = ['confirmed', 'preparing', 'out_for_delivery', 'delivered', 'cancelled'];
const money = (value) => new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(value || 0);

function parseIngredients(text) {
  return text.split('\n').map((line) => line.trim()).filter(Boolean).map((line) => {
    const [name, quantity, unit, unit_cost_cop] = line.split('|').map((part) => part.trim());
    return { name, quantity: Number(quantity), unit, unit_cost_cop: Number(unit_cost_cop) };
  });
}

function formatIngredients(items = []) {
  return items.map((item) => `${item.name}|${item.quantity}|${item.unit}|${item.unit_cost_cop}`).join('\n');
}

export default function AdminPanel({ onLogout }) {
  const [tab, setTab] = useState('products');
  const [products, setProducts] = useState([]);
  const [addons, setAddons] = useState([]);
  const [orders, setOrders] = useState([]);
  const [product, setProduct] = useState(emptyProduct);
  const [addon, setAddon] = useState(emptyAddon);
  const [editingProduct, setEditingProduct] = useState(null);
  const [editingAddon, setEditingAddon] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    setError('');
    try {
      const [productRows, addonRows, orderRows] = await Promise.all([listCocktailsAdmin(), listServiceAddonsAdmin(), listAllOrders()]);
      setProducts(productRows);
      setAddons(addonRows);
      setOrders(orderRows);
    } catch (err) { setError(getApiErrorMessage(err)); }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  async function saveProduct(event) {
    event.preventDefault();
    setBusy(true); setNotice(''); setError('');
    let saved = null;
    try {
      const payload = {
        name: product.name.trim(), description: product.description.trim(), category: product.category.trim(),
        price_cop: Number(product.price_cop), instructions: product.instructions,
        ingredients: parseIngredients(product.ingredientsText), image: product.image.trim(), is_available: product.is_available,
      };
      saved = editingProduct ? await updateCocktail(editingProduct.id, payload) : await createCocktail(payload);
      if (imageFile) await uploadCocktailImage(saved.id, imageFile);
      setProduct(emptyProduct); setEditingProduct(null); setImageFile(null);
      setNotice('Producto guardado.'); await refresh();
    } catch (err) {
      if (saved && !editingProduct) {
        setProduct(emptyProduct); setImageFile(null); await refresh();
      }
      setError(saved ? `El producto se guardó, pero la imagen no pudo cargarse. ${getApiErrorMessage(err)}` : getApiErrorMessage(err, 'No fue posible guardar el producto.'));
    }
    finally { setBusy(false); }
  }

  function editProduct(row) {
    setEditingProduct(row);
    setProduct({ ...row, price_cop: String(row.price_cop), ingredientsText: formatIngredients(row.ingredients) });
    setImageFile(null);
    setTab('products');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  async function removeProduct(row) {
    if (!window.confirm(`¿Eliminar ${row.name}?`)) return;
    try { await deleteCocktail(row.id); setNotice('Producto eliminado.'); await refresh(); }
    catch (err) { setError(getApiErrorMessage(err)); }
  }

  async function saveAddon(event) {
    event.preventDefault(); setError(''); setNotice('');
    try {
      const payload = { name: addon.name.trim(), description: addon.description.trim(), price_cop: Number(addon.price_cop), is_active: true };
      if (editingAddon) await updateServiceAddon(editingAddon.id, payload);
      else await createServiceAddon(payload);
      setAddon(emptyAddon); setEditingAddon(null); setNotice('Servicio adicional guardado.'); await refresh();
    } catch (err) { setError(getApiErrorMessage(err)); }
  }

  async function changeStatus(orderId, value) {
    try { await updateOrderStatus(orderId, value); setNotice('Estado del pedido actualizado.'); await refresh(); }
    catch (err) { setError(getApiErrorMessage(err)); }
  }

  return (
    <main className="admin-container">
      <div className="admin-header">
        <div><p className="eyebrow">Espacio del equipo</p><h1>Administración</h1></div>
        <button className="button button-quiet" onClick={onLogout}>Cerrar sesión</button>
      </div>
      <div className="admin-tabs" role="tablist" aria-label="Secciones de administración">
        {[['products', 'Productos'], ['addons', 'Servicios'], ['orders', `Pedidos (${orders.length})`]].map(([key, label]) =>
          <button key={key} role="tab" aria-selected={tab === key} className={tab === key ? 'active' : ''} onClick={() => setTab(key)}>{label}</button>)}
      </div>
      {error && <p className="notice error-msg" role="alert">{error}</p>}{notice && <p className="notice success-msg" role="status">{notice}</p>}

      {tab === 'products' && <section className="admin-section">
        <h2>{editingProduct ? 'Editar producto' : 'Agregar producto al menú'}</h2>
        <p className="muted">Define precios reales y el costo unitario de cada ingrediente. Formato por línea: <code>Ingrediente|cantidad|unidad|costo COP por unidad</code>.</p>
        <form className="admin-form" onSubmit={saveProduct}>
          <label>Nombre<input value={product.name} onChange={(e) => setProduct({ ...product, name: e.target.value })} required minLength="2" /></label>
          <label>Categoría<input value={product.category} onChange={(e) => setProduct({ ...product, category: e.target.value })} required /></label>
          <label>Precio de venta (COP)<input type="number" min="1" value={product.price_cop} onChange={(e) => setProduct({ ...product, price_cop: e.target.value })} required /></label>
          <label className="wide-field">Descripción<textarea value={product.description} onChange={(e) => setProduct({ ...product, description: e.target.value })} required /></label>
          <label className="wide-field">Ingredientes y costos<textarea value={product.ingredientsText} onChange={(e) => setProduct({ ...product, ingredientsText: e.target.value })} placeholder={'Ron|50|ml|2500\nLimón|1|unidad|800'} required rows="4" /></label>
          <label className="wide-field">Preparación<textarea value={product.instructions} onChange={(e) => setProduct({ ...product, instructions: e.target.value })} rows="3" /></label>
          <label className="wide-field">URL de imagen existente (opcional)<input value={product.image} onChange={(e) => setProduct({ ...product, image: e.target.value })} /></label>
          <label className="wide-field">Subir imagen JPG, PNG, GIF o WebP (máximo 5 MB)<input type="file" accept="image/jpeg,image/png,image/gif,image/webp" onChange={(e) => setImageFile(e.target.files?.[0] || null)} /></label>
          <label className="check-label"><input type="checkbox" checked={product.is_available} onChange={(e) => setProduct({ ...product, is_available: e.target.checked })} /> Disponible en el menú</label>
          <div className="wide-field form-actions"><button className="button button-primary" disabled={busy}>{busy ? 'Guardando…' : 'Guardar producto'}</button>{editingProduct && <button type="button" className="button button-quiet" onClick={() => { setProduct(emptyProduct); setEditingProduct(null); setImageFile(null); }}>Cancelar edición</button>}</div>
        </form>
        <h2>Productos guardados</h2>
        <div className="admin-list">{products.map((row) => <article className="admin-row" key={row.id}><div><strong>{row.name}</strong><p>{row.category} · Venta {money(row.price_cop)} · Costo estimado {money(row.estimated_cost_cop)} · {row.is_available ? 'Disponible' : 'Oculto'}</p></div><div className="row-actions"><button className="button button-quiet" onClick={() => editProduct(row)}>Editar</button><button className="button button-danger" onClick={() => removeProduct(row)}>Eliminar</button></div></article>)}{!products.length && <p className="empty-state">No hay productos guardados todavía.</p>}</div>
      </section>}

      {tab === 'addons' && <section className="admin-section"><h2>Servicios adicionales</h2><form className="admin-form" onSubmit={saveAddon}>
        <label>Nombre<input value={addon.name} onChange={(e) => setAddon({ ...addon, name: e.target.value })} required /></label>
        <label>Precio (COP)<input type="number" min="0" value={addon.price_cop} onChange={(e) => setAddon({ ...addon, price_cop: e.target.value })} required /></label>
        <label className="wide-field">Descripción<textarea value={addon.description} onChange={(e) => setAddon({ ...addon, description: e.target.value })} /></label>
        <div className="wide-field form-actions"><button className="button button-primary">{editingAddon ? 'Actualizar servicio' : 'Agregar servicio'}</button>{editingAddon && <button type="button" className="button button-quiet" onClick={() => { setAddon(emptyAddon); setEditingAddon(null); }}>Cancelar</button>}</div>
      </form><div className="admin-list">{addons.map((row) => <article className="admin-row" key={row.id}><div><strong>{row.name}</strong><p>{row.description} · {money(row.price_cop)} · {row.is_active ? 'Activo' : 'Inactivo'}</p></div><div className="row-actions"><button className="button button-quiet" onClick={() => { setEditingAddon(row); setAddon({ name: row.name, description: row.description, price_cop: String(row.price_cop) }); }}>Editar</button>{row.is_active && <button className="button button-danger" onClick={async () => { await deleteServiceAddon(row.id); refresh(); }}>Desactivar</button>}</div></article>)}{!addons.length && <p className="empty-state">Aún no hay servicios adicionales configurados.</p>}</div></section>}

      {tab === 'orders' && <section className="admin-section"><h2>Pedidos recibidos</h2><div className="admin-list">{orders.map((row) => <article className="admin-row order-row" key={row.id}><div><strong>Pedido #{row.id} · {row.customer_name || row.customer_username || 'Cliente'}</strong><p>{row.customer_phone || 'Sin teléfono'} · {row.delivery_address}</p><p>{row.items.map((item) => `${item.quantity} × ${item.name}`).join(', ')}</p><p>{money(row.total_cop)} · Pago: {row.payment_status} · {row.delivery_scheduled_at ? new Date(row.delivery_scheduled_at).toLocaleString('es-CO') : 'Sin hora programada'}</p></div><label>Estado<select value={row.status} onChange={(e) => changeStatus(row.id, e.target.value)}>{[row.status, ...orderStatuses.filter((s) => s !== row.status)].map((s) => <option key={s} value={s}>{s.replaceAll('_', ' ')}</option>)}</select></label></article>)}{!orders.length && <p className="empty-state">Todavía no hay pedidos.</p>}</div></section>}
    </main>
  );
}

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { GlassWater, Search, ShoppingBag, User, Settings, X, Plus, Minus, Menu, LogOut } from 'lucide-react';
import { getBusinessInfo, listServiceAddons, searchExternalRecipes } from './api/business';
import { listCocktailCategories, listCocktails } from './api/cocktails';
import { createOrder, getPaymentConfig, listMyOrders } from './api/orders';
import { getApiErrorMessage } from './api/http';
import { useAuth } from './features/auth/AuthContext';
import { resolveImageUrl } from './utils/images';
import AdminPanel from './components/admin/AdminPanel';
import Login from './components/admin/Login';

const initialCart = () => {
  try { return JSON.parse(localStorage.getItem('grillo-cart') || '[]'); } catch { return []; }
};
const money = (value) => new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(value || 0);

function RegisterForm({ onCancel, onDone }) {
  const { register } = useAuth();
  const [fields, setFields] = useState({ username: '', email: '', full_name: '', phone: '', national_id: '', address: '', city: '', password: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const set = (key) => (event) => setFields((old) => ({ ...old, [key]: event.target.value }));
  async function submit(event) {
    event.preventDefault(); setError(''); setBusy(true);
    try { await register(fields); onDone(); }
    catch (err) { setError(getApiErrorMessage(err, 'No fue posible crear la cuenta.')); }
    finally { setBusy(false); }
  }
  return <section className="auth-card register-card"><h2>Crear cuenta</h2><p>Usaremos estos datos para gestionar tu pedido y la entrega.</p>
    <form onSubmit={submit} className="register-form">
      <label>Nombre completo<input autoComplete="name" value={fields.full_name} onChange={set('full_name')} required /></label>
      <label>Usuario<input autoComplete="username" value={fields.username} onChange={set('username')} pattern="[A-Za-z0-9_.-]{3,50}" required /></label>
      <label>Correo electrónico<input type="email" autoComplete="email" value={fields.email} onChange={set('email')} required /></label>
      <label>Teléfono<input type="tel" autoComplete="tel" value={fields.phone} onChange={set('phone')} required /></label>
      <label>Documento de identidad<input value={fields.national_id} onChange={set('national_id')} required /></label>
      <label>Ciudad<input autoComplete="address-level2" value={fields.city} onChange={set('city')} required /></label>
      <label className="wide-field">Dirección<input autoComplete="street-address" value={fields.address} onChange={set('address')} required /></label>
      <label className="wide-field">Contraseña (mínimo 12 caracteres)<input type="password" autoComplete="new-password" minLength="12" maxLength="128" value={fields.password} onChange={set('password')} required /></label>
      {error && <p className="error-msg wide-field" role="alert">{error}</p>}
      <button className="button button-primary wide-field" disabled={busy}>{busy ? 'Creando cuenta…' : 'Crear cuenta'}</button>
      <button type="button" className="button button-quiet wide-field" onClick={onCancel}>Volver</button>
    </form>
  </section>;
}

function App() {
  const { user, loading: authLoading, logout } = useAuth();
  const [view, setView] = useState('home');
  const [showAuth, setShowAuth] = useState('');
  const [mobileMenu, setMobileMenu] = useState(false);
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [addons, setAddons] = useState([]);
  const [business, setBusiness] = useState({ name: 'Estanco y Coctelería El Grillo' });
  const [cart, setCart] = useState(initialCart);
  const [orders, setOrders] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [externalSearch, setExternalSearch] = useState('');
  const [recipes, setRecipes] = useState([]);
  const [checkoutOpen, setCheckoutOpen] = useState(false);
  const [checkout, setCheckout] = useState({ address: '', scheduled: '', notes: '', payment: 'cash_on_delivery', addon_ids: [] });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [cookieNotice, setCookieNotice] = useState(() => !localStorage.getItem('grillo-cookie-notice'));
  const [paymentReturn, setPaymentReturn] = useState(() => new URLSearchParams(window.location.search).get('pedido'));

  const refreshCatalog = useCallback(async (search = '', category = '') => {
    setLoading(true); setError('');
    try {
      const page = await listCocktails({ search, category: category || undefined, page: 1, page_size: 48 });
      setProducts(page.items || []);
    } catch (err) { setError(getApiErrorMessage(err, 'No se pudo cargar el menú.')); }
    finally { setLoading(false); }
  }, []);

  const refreshOrders = useCallback(async () => {
    if (!user) { setOrders([]); return; }
    try { setOrders(await listMyOrders()); } catch (err) { setError(getApiErrorMessage(err)); }
  }, [user]);

  useEffect(() => {
    listCocktailCategories().then(setCategories).catch(() => {});
    listServiceAddons().then(setAddons).catch(() => {});
    getBusinessInfo().then(setBusiness).catch(() => {});
    refreshCatalog();
  }, [refreshCatalog]);

  useEffect(() => { localStorage.setItem('grillo-cart', JSON.stringify(cart)); }, [cart]);
  useEffect(() => { if (user) setCheckout((old) => ({ ...old, address: old.address || [user.address, user.city].filter(Boolean).join(', ') })); refreshOrders(); }, [user, refreshOrders]);
  useEffect(() => {
    if (!paymentReturn) return;
    setView('orders');
    if (user) {
      refreshOrders();
      setMessage(`Volviste de Wompi. El estado del pedido #${paymentReturn} se actualiza al recibir la confirmación del pago.`);
      setPaymentReturn(null);
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, [paymentReturn, user, refreshOrders]);
  useEffect(() => {
    if (user && showAuth) {
      setShowAuth('');
      if (['admin', 'editor'].includes(user.role)) setView('admin');
    }
  }, [user, showAuth]);

  const cartCount = useMemo(() => cart.reduce((sum, item) => sum + item.quantity, 0), [cart]);
  const subtotal = useMemo(() => cart.reduce((sum, item) => sum + item.price_cop * item.quantity, 0), [cart]);
  const isStaff = user && ['admin', 'editor'].includes(user.role);

  function navigate(next) { setView(next); setMobileMenu(false); setMessage(''); setError(''); window.scrollTo({ top: 0, behavior: 'smooth' }); }
  function addToCart(item) {
    setCart((old) => {
      const found = old.find((row) => row.id === item.id);
      return found ? old.map((row) => row.id === item.id ? { ...row, quantity: row.quantity + 1 } : row) : [...old, { id: item.id, name: item.name, price_cop: item.price_cop, image: item.image, quantity: 1 }];
    });
    setMessage(`${item.name} se agregó al carrito.`);
  }
  function changeQuantity(id, difference) {
    setCart((old) => old.map((row) => row.id === id ? { ...row, quantity: row.quantity + difference } : row).filter((row) => row.quantity > 0));
  }
  function handleSearch(event) { event.preventDefault(); setSelectedCategory(''); refreshCatalog(searchTerm, ''); }
  async function searchRecipes(event) {
    event.preventDefault(); setLoading(true); setError('');
    try { const data = await searchExternalRecipes({ search: externalSearch.trim() }); setRecipes(data.items || []); }
    catch (err) { setError(getApiErrorMessage(err, 'No se pudo consultar el recetario externo.')); }
    finally { setLoading(false); }
  }

  async function submitOrder(event) {
    event.preventDefault(); setError(''); setMessage('');
    if (!user) { setCheckoutOpen(false); setShowAuth('login'); return; }
    try {
      const created = await createOrder({
        items: cart.map((item) => ({ cocktail_id: item.id, quantity: item.quantity })),
        addon_ids: checkout.addon_ids,
        delivery_address: checkout.address,
        delivery_scheduled_at: checkout.scheduled ? new Date(checkout.scheduled).toISOString() : null,
        delivery_notes: checkout.notes,
        payment_method: checkout.payment,
      });
      setCart([]); setCheckoutOpen(false); await refreshOrders();
      if (checkout.payment === 'wompi') {
        try {
          const config = await getPaymentConfig(created.id);
          window.location.assign(config.checkout_url);
          return;
        } catch (paymentError) {
          navigate('orders');
          setMessage(`Pedido #${created.id} creado y pendiente de pago. ${getApiErrorMessage(paymentError, 'El pago en línea no está disponible ahora.')}`);
          return;
        }
      }
      navigate('orders');
      setMessage(`Pedido #${created.id} recibido. Te contactaremos para coordinar la entrega.`);
    } catch (err) { setError(getApiErrorMessage(err, 'No se pudo crear el pedido.')); }
  }

  async function retryPayment(orderId) {
    try { const config = await getPaymentConfig(orderId); window.location.assign(config.checkout_url); }
    catch (err) { setError(getApiErrorMessage(err, 'No fue posible iniciar el pago.')); }
  }

  async function signOut() { await logout(); setMessage('Sesión cerrada.'); navigate('home'); }

  const nav = <>
    <a href="#menu" onClick={(e) => { e.preventDefault(); navigate('home'); }}>Inicio</a>
    <a href="#catalogo" onClick={(e) => { e.preventDefault(); navigate('home'); document.getElementById('catalogo')?.scrollIntoView({ behavior: 'smooth' }); }}>Menú</a>
    <a href="#recetas" onClick={(e) => { e.preventDefault(); navigate('recipes'); }}>Recetas</a>
    <a href="#about" onClick={(e) => { e.preventDefault(); navigate('about'); }}>Nosotros</a>
    <a href="#contact" onClick={(e) => { e.preventDefault(); navigate('contact'); }}>Contacto</a>
    {user && <button className="nav-action" onClick={() => navigate('orders')}>Mis pedidos</button>}
    {isStaff && <button className="nav-action" onClick={() => navigate('admin')}><Settings size={16} /> Administración</button>}
  </>;

  return <div className="app-root">
    <header className="navbar">
      <button className="nav-logo" onClick={() => navigate('home')}><GlassWater size={30} /><span>{business.name || 'El Grillo'}</span></button>
      <nav className={`nav-links ${mobileMenu ? 'open' : ''}`}>{nav}</nav>
      <div className="nav-tools">
        <button className="nav-action cart-shortcut" onClick={() => navigate('cart')} aria-label={`Carrito, ${cartCount} productos`}><ShoppingBag size={19} /><span>Carrito</span><b>{cartCount}</b></button>
        {user ? <button className="nav-action account-action" onClick={signOut} title={`Cerrar sesión de ${user.username}`}><LogOut size={18} /><span>Salir</span></button> : <button className="nav-action account-action" onClick={() => setShowAuth('login')}><User size={18} /><span>Entrar</span></button>}
        <button className="mobile-toggle" onClick={() => setMobileMenu(!mobileMenu)} aria-label="Abrir menú"><Menu /></button>
      </div>
    </header>

    {message && <p className="notice success-msg" role="status">{message}<button onClick={() => setMessage('')} aria-label="Cerrar">×</button></p>}
    {error && <p className="notice error-msg" role="alert">{error}<button onClick={() => setError('')} aria-label="Cerrar">×</button></p>}

    {view === 'home' && <>
      <section className="hero" id="menu"><p className="eyebrow">Sabor para compartir</p><h1>Un buen momento<br /><span>empieza con un brindis.</span></h1><p>Explora el menú de {business.name || 'El Grillo'}, arma tu pedido y elige cuándo recibirlo.</p><form className="search-wrapper" onSubmit={handleSearch}><Search size={19} /><input aria-label="Buscar en el menú" placeholder="Busca un producto del menú…" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} /><button className="button button-primary">Buscar</button></form></section>
      <section className="catalog-section" id="catalogo"><div className="section-heading"><div><p className="eyebrow">Menú del negocio</p><h2>El menú de El Grillo</h2></div><button className="text-button" onClick={() => { setSearchTerm(''); setSelectedCategory(''); refreshCatalog(); }}>Ver todo</button></div>
        {categories.length > 0 && <div className="categories"><button className={!selectedCategory ? 'cat-pill active' : 'cat-pill'} onClick={() => { setSelectedCategory(''); refreshCatalog(searchTerm); }}>Todas</button>{categories.map((category) => <button key={category} className={selectedCategory === category ? 'cat-pill active' : 'cat-pill'} onClick={() => { setSelectedCategory(category); refreshCatalog(searchTerm, category); }}>{category}</button>)}</div>}
        {loading && <p className="empty-state">Cargando menú…</p>}
        {!loading && !products.length && <div className="empty-state"><GlassWater size={28} /><h3>El menú se está preparando</h3><p>Pronto verás aquí los productos disponibles. El equipo debe publicar productos con precios vigentes.</p></div>}
        <div className="cocktail-grid">{products.map((item) => <article className="cocktail-card" key={item.id}><button className="card-open" onClick={() => setSelectedProduct(item)}><img src={resolveImageUrl(item.image)} alt={item.name} className="card-image" /><span className="card-content"><span className="card-tag">{item.category}</span><strong className="card-title">{item.name}</strong><span className="card-description">{item.description}</span><b className="product-price">{money(item.price_cop)}</b></span></button><button className="add-button" onClick={() => addToCart(item)}><Plus size={17} /> Agregar</button></article>)}</div>
      </section>
      <section className="feature-band" id="recetas"><div><p className="eyebrow">Inspírate</p><h2>¿Quieres explorar recetas?</h2><p>Consulta el catálogo externo de preparaciones y sus ingredientes.</p></div><button className="button button-light" onClick={() => navigate('recipes')}>Ver recetas</button></section>
      <section className="about-preview"><p className="eyebrow">El negocio</p><h2>Un espacio para compartir</h2><p>{business.about || 'Conoce el menú y servicios de nuestro negocio.'}</p><button className="text-button" onClick={() => navigate('about')}>Conócenos</button></section>
    </>}

    {view === 'recipes' && <main className="page-container"><p className="eyebrow">Catálogo de consulta</p><h1>Recetas de cócteles</h1><p className="muted">Las recetas se consultan desde un servicio externo y no forman parte del menú de venta.</p><form className="search-wrapper recipe-search" onSubmit={searchRecipes}><Search /><input placeholder="Busca por nombre…" value={externalSearch} onChange={(e) => setExternalSearch(e.target.value)} required /><button className="button button-primary">Buscar</button></form><div className="recipe-grid">{recipes.map((recipe) => <article className="recipe-card" key={recipe.idDrink}><img src={recipe.strDrinkThumb} alt={recipe.strDrink} /><div><span className="card-tag">{recipe.strCategory || recipe.strAlcoholic || 'Receta'}</span><h2>{recipe.strDrink}</h2><button className="text-button" onClick={() => setSelectedProduct({ external: true, ...recipe })}>Ver ingredientes</button></div></article>)}</div>{!recipes.length && <p className="empty-state">Escribe el nombre de una receta para consultar el catálogo externo.</p>}</main>}

    {view === 'about' && <main className="page-container info-page"><p className="eyebrow">Sobre nosotros</p><h1>{business.name || 'El Grillo'}</h1><p>{business.about || 'Conoce los productos, servicios y novedades del negocio.'}</p><h2>Una experiencia sencilla</h2><p>Consulta el menú, revisa las recetas disponibles y organiza un pedido con entrega programada desde la misma plataforma.</p></main>}
    {view === 'contact' && <main className="page-container info-page"><p className="eyebrow">Estamos para ayudarte</p><h1>Contacto</h1><p>Escríbenos o llámanos con los datos de contacto del negocio.</p><div className="contact-list">{business.phone && <p><strong>Teléfono</strong><a href={`tel:${business.phone}`}>{business.phone}</a></p>}{business.email && <p><strong>Correo</strong><a href={`mailto:${business.email}`}>{business.email}</a></p>}{business.address && <p><strong>Dirección</strong><span>{business.address}</span></p>}{[['Instagram', business.instagram, 'https://instagram.com/'], ['Facebook', business.facebook, 'https://facebook.com/'], ['TikTok', business.tiktok, 'https://tiktok.com/@']].map(([label, value, base]) => value && <p key={label}><strong>{label}</strong><a href={value.startsWith('http') ? value : `${base}${value.replace(/^@/, '')}`} target="_blank" rel="noreferrer">{value}</a></p>)}{!business.phone && !business.email && !business.address && !business.instagram && !business.facebook && !business.tiktok && <p className="empty-state">El equipo todavía no ha configurado los datos de contacto.</p>}</div></main>}

    {view === 'cart' && <main className="page-container"><p className="eyebrow">Tu selección</p><h1>Carrito</h1>{!cart.length ? <p className="empty-state">Tu carrito está vacío. <button className="text-button" onClick={() => navigate('home')}>Ver menú</button></p> : <div className="cart-layout"><div className="cart-list">{cart.map((item) => <article className="cart-row" key={item.id}><img src={resolveImageUrl(item.image)} alt="" /><div className="cart-item-info"><strong>{item.name}</strong><span>{money(item.price_cop)} cada uno</span></div><div className="quantity-control"><button onClick={() => changeQuantity(item.id, -1)} aria-label={`Quitar uno de ${item.name}`}><Minus size={16} /></button><b>{item.quantity}</b><button onClick={() => changeQuantity(item.id, 1)} aria-label={`Agregar uno de ${item.name}`}><Plus size={16} /></button></div><strong>{money(item.price_cop * item.quantity)}</strong></article>)}</div><aside className="summary-card"><h2>Resumen</h2><p><span>Subtotal</span><strong>{money(subtotal)}</strong></p><p className="muted">La entrega y los servicios seleccionados se confirman al crear el pedido.</p><button className="button button-primary" onClick={() => user ? setCheckoutOpen(true) : setShowAuth('login')}>Continuar con el pedido</button>{!user && <button className="text-button" onClick={() => setShowAuth('register')}>Crear cuenta para continuar</button>}</aside></div>}</main>}

    {view === 'orders' && <main className="page-container"><p className="eyebrow">Tu actividad</p><h1>Mis pedidos</h1>{user ? <>{orders.map((order) => <article className="order-card" key={order.id}><div className="section-heading"><div><h2>Pedido #{order.id}</h2><p>{new Date(order.created_at).toLocaleString('es-CO')}</p></div><span className={`status-pill status-${order.status}`}>{order.status.replaceAll('_', ' ')}</span></div><p>{order.items.map((item) => `${item.quantity} × ${item.name}`).join(', ')}</p>{order.addons.length > 0 && <p>Servicios: {order.addons.map((addon) => addon.name).join(', ')}</p>}<p>Entrega: {order.delivery_address}{order.delivery_scheduled_at ? ` · ${new Date(order.delivery_scheduled_at).toLocaleString('es-CO')}` : ''}</p><div className="section-heading"><strong>{money(order.total_cop)}</strong><span>Pago: {order.payment_status.replaceAll('_', ' ')}</span></div>{order.payment_method === 'wompi' && order.payment_status === 'pending' && <button className="button button-primary" onClick={() => retryPayment(order.id)}>Continuar pago en línea</button>}</article>)}{!orders.length && <p className="empty-state">Todavía no tienes pedidos.</p>}</> : <div className="empty-state"><p>Inicia sesión para consultar tus pedidos.</p><button className="button button-primary" onClick={() => setShowAuth('login')}>Iniciar sesión</button></div>}</main>}

    {view === 'admin' && (isStaff ? <AdminPanel onLogout={signOut} /> : <main className="page-container"><p className="eyebrow">Acceso de personal</p><h1>Administración</h1>{user ? <p>Tu cuenta no tiene permisos para administrar el menú.</p> : <Login onCancel={() => navigate('home')} />}</main>)}

    <footer className="footer"><div className="footer-brand"><GlassWater size={28} /><strong>{business.name || 'El Grillo'}</strong></div><div className="footer-links"><button onClick={() => navigate('about')}>Nosotros</button><button onClick={() => navigate('contact')}>Contacto</button><button onClick={() => setShowAuth(user ? '' : 'login')}>{user ? user.full_name : 'Mi cuenta'}</button></div><p>© {new Date().getFullYear()} {business.name || 'El Grillo'}. Catálogo y pedidos en línea.</p></footer>

    {showAuth && <div className="modal-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setShowAuth(''); }}><div className="modal-content auth-modal"><button className="modal-close" onClick={() => setShowAuth('')} aria-label="Cerrar"><X /></button>{showAuth === 'login' ? <><Login onCancel={() => setShowAuth('')} /><p className="auth-switch">¿Aún no tienes cuenta? <button className="text-button" onClick={() => setShowAuth('register')}>Regístrate</button></p></> : <RegisterForm onCancel={() => setShowAuth('')} onDone={() => setShowAuth('')} />}</div></div>}

    {checkoutOpen && <div className="modal-overlay" role="presentation"><div className="modal-content checkout-modal"><button className="modal-close" onClick={() => setCheckoutOpen(false)} aria-label="Cerrar"><X /></button><p className="eyebrow">Último paso</p><h2>Coordina tu pedido</h2><form onSubmit={submitOrder} className="checkout-form"><label>Dirección de entrega<input value={checkout.address} onChange={(e) => setCheckout({ ...checkout, address: e.target.value })} required minLength="5" /></label><label>Fecha y hora de entrega (opcional)<input type="datetime-local" value={checkout.scheduled} onChange={(e) => setCheckout({ ...checkout, scheduled: e.target.value })} /></label><label>Instrucciones de entrega<textarea value={checkout.notes} onChange={(e) => setCheckout({ ...checkout, notes: e.target.value })} maxLength="500" /></label>{addons.length > 0 && <fieldset><legend>Servicios adicionales</legend>{addons.map((addon) => <label className="addon-choice" key={addon.id}><input type="checkbox" checked={checkout.addon_ids.includes(addon.id)} onChange={(e) => setCheckout((old) => ({ ...old, addon_ids: e.target.checked ? [...old.addon_ids, addon.id] : old.addon_ids.filter((id) => id !== addon.id) }))} /><span>{addon.name} · {money(addon.price_cop)}<small>{addon.description}</small></span></label>)}</fieldset>}<label>Método de pago<select value={checkout.payment} onChange={(e) => setCheckout({ ...checkout, payment: e.target.value })}><option value="cash_on_delivery">Pago contra entrega</option><option value="wompi">Pago en línea con Wompi</option></select></label><div className="summary-total"><span>Total de productos</span><strong>{money(subtotal + addons.filter((addon) => checkout.addon_ids.includes(addon.id)).reduce((total, addon) => total + addon.price_cop, 0))}</strong></div><button className="button button-primary">Crear pedido</button></form></div></div>}

    {selectedProduct && <div className="modal-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setSelectedProduct(null); }}><article className="modal-content detail-modal"><button className="modal-close" onClick={() => setSelectedProduct(null)} aria-label="Cerrar"><X /></button><img className="modal-img" src={resolveImageUrl(selectedProduct.image || selectedProduct.strDrinkThumb)} alt={selectedProduct.name || selectedProduct.strDrink} /><div className="modal-info"><span className="card-tag">{selectedProduct.category || selectedProduct.strCategory || 'Receta externa'}</span><h2>{selectedProduct.name || selectedProduct.strDrink}</h2><p>{selectedProduct.description || (selectedProduct.external ? selectedProduct.strInstructions || 'Receta consultada en el catálogo externo.' : '')}</p><h3>Ingredientes</h3><ul className="ingredient-list">{selectedProduct.external ? Array.from({ length: 15 }, (_, index) => index + 1).filter((i) => selectedProduct[`strIngredient${i}`]).map((i) => <li className="ingredient-list-item" key={i}><span>{selectedProduct[`strIngredient${i}`]}</span><strong>{selectedProduct[`strMeasure${i}`]}</strong></li>) : (selectedProduct.ingredients || []).map((item, index) => <li className="ingredient-list-item" key={`${item.name}-${index}`}><span>{item.name}</span><strong>{item.quantity} {item.unit}</strong></li>)}</ul>{!selectedProduct.external && <><strong className="product-price">{money(selectedProduct.price_cop)}</strong><button className="button button-primary" onClick={() => { addToCart(selectedProduct); setSelectedProduct(null); }}>Agregar al carrito</button></>}</div></article></div>}

    {cookieNotice && <aside className="cookie-notice" role="status"><p>Esta aplicación usa una cookie HTTP-only necesaria para mantener tu sesión al ingresar. El carrito se guarda en este dispositivo; no usamos cookies de analítica.</p><button className="button button-primary" onClick={() => { localStorage.setItem('grillo-cookie-notice', 'seen'); setCookieNotice(false); }}>Entendido</button></aside>}
    {authLoading && <div className="auth-loading" aria-live="polite">Comprobando sesión…</div>}
  </div>;
}

export default App;

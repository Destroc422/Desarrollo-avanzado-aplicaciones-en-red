import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, GlassWater, X, Star, Clock, Info, Settings } from 'lucide-react';
import AdminPanel from './components/admin/AdminPanel';
import Login from './components/admin/Login';
import './App.css';

const CATEGORIES = ['Ordinary Drink', 'Cocktail', 'Shake', 'Other/Unknown'];

function App() {
  const [isAdmin, setIsAdmin] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'));
  const [cocktails, setCocktails] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedCocktail, setSelectedCocktail] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchCocktails = async (query = '', category = 'All') => {
    setLoading(true);
    try {
      let endpoint = '';
      if (query) {
        endpoint = `https://www.thecocktaildb.com/api/json/v1/1/search.php?s=${query}`;
      } else if (category !== 'All') {
        endpoint = `https://www.thecocktaildb.com/api/json/v1/1/filter.php?c=${category}`;
      } else {
        const randoms = await Promise.all([
          axios.get('https://www.thecocktaildb.com/api/json/v1/1/random.php'),
          axios.get('https://www.thecocktaildb.com/api/json/v1/1/random.php'),
          axios.get('https://www.thecocktaildb.com/api/json/v1/1/random.php'),
          axios.get('https://www.thecocktaildb.com/api/json/v1/1/random.php'),
          axios.get('https://www.thecocktaildb.com/api/json/v1/1/random.php'),
          axios.get('https://www.thecocktaildb.com/api/json/v1/1/random.php'),
        ]);
        setCocktails(randoms.map(r => r.data.drinks[0]));
        setLoading(false);
        return;
      }

      const response = await axios.get(endpoint);
      const data = response.data.drinks;
      setCocktails(data ? (Array.isArray(data) ? data : [data[0]]) : []);
    } catch (error) {
      console.error("Error fetching cocktails:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCocktails();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    setSelectedCategory('All');
    fetchCocktails(searchTerm);
  };

  const handleCategoryClick = (cat) => {
    setSelectedCategory(cat);
    setSearchTerm('');
    fetchCocktails('', cat);
  };

  const openDetails = async (id) => {
    setLoading(true);
    try {
      const response = await axios.get(`https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i=${id}`);
      setSelectedCocktail(response.data.drinks[0]);
    } catch (error) {
      console.error("Error fetching details:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setIsAdmin(false);
  };

  if (isAdmin) {
    if (!isAuthenticated) {
      return <Login onLoginSuccess={() => { setIsAuthenticated(true); }} />;
    }
    return <AdminPanel onLogout={handleLogout} />;
  }

  return (
    <div className="app-root">
      <nav className="navbar">
        <div className="nav-logo" onClick={() => window.location.reload()}>
          <GlassWater size={32} />
          <span>GrilloCocktails</span>
        </div>
        <ul className="nav-links">
          <li><a href="#home">Inicio</a></li>
          <li><a href="#catalog">Catálogo</a></li>
          <li><a href="#about">Sobre Nosotros</a></li>
          <li><a href="#contact">Contacto</a></li>
          <li onClick={() => setIsAdmin(true)} style={{cursor: 'pointer', color: 'var(--primary)'}}>
            <Settings size={20} />
          </li>
        </ul>
      </nav>

      <section className="hero" id="home">
        <h1>El Arte de la Coctelería <br/><span style={{color: 'var(--primary)'}}>en Verde Grillo</span></h1>
        <p>Descubre la mezcla perfecta entre sofisticación y frescura. Explora nuestra colección curada de cócteles premium.</p>
        <form className="search-wrapper" onSubmit={handleSearch}>
          <input 
            className="search-input"
            type="text" 
            placeholder="Busca tu bebida favorita..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button type="submit" className="search-btn">
            <Search size={20} />
          </button>
        </form>
      </section>

      <div className="categories">
        <div 
          className={`cat-pill ${selectedCategory === 'All' ? 'active' : ''}`} 
          onClick={() => handleCategoryClick('All')}
        >
          Todos
        </div>
        {CATEGORIES.map(cat => (
          <div 
            key={cat} 
            className={`cat-pill ${selectedCategory === cat ? 'active' : ''}`} 
            onClick={() => handleCategoryClick(cat)}
          >
            {cat}
          </div>
        ))}
      </div>

      <h2 className="section-title" id="catalog">Explora el Catálogo</h2>
      
      {loading && cocktails.length === 0 ? (
        <div style={{textAlign: 'center', padding: '3rem'}}>Cargando experiencias...</div>
      ) : (
        <div className="cocktail-grid">
          {cocktails.map((cocktail) => (
            <div key={cocktail.idDrink} className="cocktail-card" onClick={() => openDetails(cocktail.idDrink)}>
              <img src={cocktail.strDrinkThumb} alt={cocktail.strDrink} className="card-image" />
              <div className="card-content">
                <span className="card-tag">{cocktail.strCategory || 'Premium'}</span>
                <h3 className="card-title">{cocktail.strDrink}</h3>
                <div style={{display: 'flex', gap: '10px', color: 'var(--text-muted)', fontSize: '0.8rem'}}>
                  <span style={{display: 'flex', alignItems: 'center', gap: '4px'}}><Star size={14} fill="currentColor"/> 4.8</span>
                  <span style={{display: 'flex', alignItems: 'center', gap: '4px'}}><Clock size={14}/> 5-10 min</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedCocktail && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button className="modal-close" onClick={() => setSelectedCocktail(null)}>X</button>
            <img src={selectedCocktail.strDrinkThumb} className="modal-img" alt={selectedCocktail.strDrink} />
            <div className="modal-info">
              <h2 style={{fontSize: '2rem', marginBottom: '1rem'}}>{selectedCocktail.strDrink}</h2>
              <p style={{color: 'var(--text-muted)', marginBottom: '1.5rem'}}>{selectedCocktail.strInstructions}</p>
              
              <h4 style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem'}}>
                <Info size={20} /> Ingredientes
              </h4>
              <ul className="ingredient-list">
                {[...Array(5)].map((_, i) => {
                  const ing = selectedCocktail[`strIngredient${i+1}`];
                  const measure = selectedCocktail[`strMeasure${i+1}`];
                  if (!ing) return null;
                  return (
                    <li key={i} className="ingredient-list-item">
                      <span>{ing}</span>
                      <span style={{fontWeight: 'bold'}}>{measure || ''}</span>
                    </li>
                  );
                })}
              </ul>
            </div>
          </div>
        </div>
      )}

      <footer className="footer">
        <div className="nav-logo" style={{justifyContent: 'center', color: 'white', marginBottom: '2rem'}}>
          <GlassWater size={32} />
          <span>GrilloCocktails</span>
        </div>
        <div className="footer-links">
          <a href="#">Privacidad</a>
          <a href="#">Términos</a>
          <a href="#">Contacto</a>
        </div>
        <p style={{opacity: 0.7, fontSize: '0.9rem'}}>© 2026 GrilloCocktails Premium Experience. Todos los derechos reservados.</p>
      </footer>
    </div>
  );
}

export default App;

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Trash2, Edit, Plus, Save, X, LogOut } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000/cocktails';

function AdminPanel({ onLogout }) {
  const [cocktails, setCocktails] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCocktail, setEditingCocktail] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    ingredients: '',
    image: ''
  });

  useEffect(() => {
    fetchCocktails();
  }, []);

  const getAuthHeader = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  });

  const fetchCocktails = async () => {
    try {
      const response = await axios.get(API_BASE);
      setCocktails(response.data);
    } catch (error) {
      alert('Error fetching cocktails');
    }
  };

  const handleOpenModal = (cocktail = null) => {
    if (cocktail) {
      setEditingCocktail(cocktail);
      setFormData({
        name: cocktail.name,
        description: cocktail.description,
        ingredients: cocktail.ingredients.join(', '),
        image: cocktail.image
      });
    } else {
      setEditingCocktail(null);
      setFormData({ name: '', description: '', ingredients: '', image: '' });
    }
    setIsModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      ...formData,
      ingredients: formData.ingredients.split(',').map(i => i.trim())
    };

    try {
      if (editingCocktail) {
        await axios.put(`${API_BASE}/${editingCocktail.id}`, payload, getAuthHeader());
      } else {
        await axios.post(API_BASE, payload, getAuthHeader());
      }
      setIsModalOpen(false);
      fetchCocktails();
    } catch (error) {
      alert('Error saving cocktail. ¿Estás autenticado?');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('¿Estás seguro de eliminar este cóctel?')) {
      try {
        await axios.delete(`${API_BASE}/${id}`, getAuthHeader());
        fetchCocktails();
      } catch (error) {
        alert('Error deleting cocktail');
      }
    }
  };

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>Panel de Administración</h1>
        <div style={{display: 'flex', gap: '10px'}}>
          <button className="btn-add" onClick={() => handleOpenModal()}>
            <Plus size={20} /> Añadir Cóctel
          </button>
          <button className="btn-logout" onClick={onLogout}>
            <LogOut size={20} /> Salir
          </button>
        </div>
      </div>

      <div className="admin-table-wrapper">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Imagen</th>
              <th>Nombre</th>
              <th>Descripción</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {cocktails.map(c => (
              <tr key={c.id}>
                <td><img src={c.image} alt={c.name} className="table-img" /></td>
                <td>{c.name}</td>
                <td>{c.description}</td>
                <td className="actions">
                  <button onClick={() => handleOpenModal(c)} className="btn-edit"><Edit size={16}/></button>
                  <button onClick={() => handleDelete(c.id)} className="btn-delete"><Trash2 size={16}/></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content admin-modal">
            <button className="modal-close" onClick={() => setIsModalOpen(false)}>X</button>
            <h2>{editingCocktail ? 'Editar Cóctel' : 'Nuevo Cóctel'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nombre</label>
                <input value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>Descripción</label>
                <textarea value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>Ingredientes (separados por coma)</label>
                <input value={formData.ingredients} onChange={e => setFormData({...formData, ingredients: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>URL de Imagen</label>
                <input value={formData.image} onChange={e => setFormData({...formData, image: e.target.value})} required />
              </div>
              <button type="submit" className="btn-save">
                <Save size={20} /> Guardar Cambios
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminPanel;

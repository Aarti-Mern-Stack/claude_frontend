import { useState, useEffect } from 'react';
import api from '../api/axios';

export default function Dashboard() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ title: '', description: '' });
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState('');

  const fetchItems = async () => {
    try {
      const res = await api.get('/items');
      setItems(res.data);
    } catch {
      setError('Failed to fetch items');
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const resetForm = () => {
    setForm({ title: '', description: '' });
    setEditingId(null);
    setShowForm(false);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (editingId) {
        await api.put(`/items/${editingId}`, form);
      } else {
        await api.post('/items', form);
      }
      resetForm();
      fetchItems();
    } catch {
      setError(editingId ? 'Failed to update item' : 'Failed to create item');
    }
  };

  const handleEdit = (item) => {
    setForm({ title: item.title, description: item.description });
    setEditingId(item._id || item.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this item?')) return;
    try {
      await api.delete(`/items/${id}`);
      fetchItems();
    } catch {
      setError('Failed to delete item');
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Dashboard</h2>
        <button className="btn btn-primary" onClick={() => { resetForm(); setShowForm(true); }}>
          + Add Item
        </button>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {showForm && (
        <div className="modal-overlay" onClick={() => resetForm()}>
          <form className="item-form" onSubmit={handleSubmit} onClick={(e) => e.stopPropagation()}>
            <h3>{editingId ? 'Edit Item' : 'Add Item'}</h3>
            <div className="form-group">
              <label htmlFor="title">Title</label>
              <input
                id="title"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                rows={3}
                required
              />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary">
                {editingId ? 'Update' : 'Create'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={resetForm}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {items.length === 0 ? (
        <p className="empty-state">No items yet. Click "Add Item" to create one.</p>
      ) : (
        <div className="items-grid">
          {items.map((item) => (
            <div key={item._id || item.id} className="item-card">
              <h3>{item.title}</h3>
              <p>{item.description}</p>
              <div className="item-actions">
                <button className="btn btn-edit" onClick={() => handleEdit(item)}>Edit</button>
                <button className="btn btn-delete" onClick={() => handleDelete(item._id || item.id)}>Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

import { useState, useEffect } from 'react';
import { apiService } from '../services/api';

export default function Dashboard() {
  const [apis, setApis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [uploadData, setUploadData] = useState({ name: '', prefix: '', server_file: null, folder: null });
  const [selectedApi, setSelectedApi] = useState(null);

  const fetchApis = async () => {
    try {
      const res = await apiService.getAll();
      setApis(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApis();
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('name', uploadData.name);
    formData.append('prefix', uploadData.prefix);
    formData.append('server_file', uploadData.server_file);
    if (uploadData.folder) formData.append('folder', uploadData.folder);

    try {
      await apiService.upload(formData);
      setShowUpload(false);
      setUploadData({ name: '', prefix: '', server_file: null, folder: null });
      fetchApis();
    } catch (err) {
      alert('Upload failed');
    }
  };

  const handleStart = async (id) => {
    await apiService.start(id);
    fetchApis();
  };

  const handleStop = async (id) => {
    await apiService.stop(id);
    fetchApis();
  };

  const handleDelete = async (id) => {
    if (confirm('Delete this API?')) {
      await apiService.delete(id);
      fetchApis();
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return '#22c55e';
      case 'stopped': return '#6b7280';
      case 'error': return '#ef4444';
      default: return '#6b7280';
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="dashboard">
      <header className="header">
        <h1>API ROUTER</h1>
        <button className="btn-primary" onClick={() => setShowUpload(true)}>
          + Add API
        </button>
      </header>

      {showUpload && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Upload New API</h2>
            <form onSubmit={handleUpload}>
              <input
                type="text"
                placeholder="API Name"
                value={uploadData.name}
                onChange={(e) => setUploadData({...uploadData, name: e.target.value})}
                required
              />
              <input
                type="text"
                placeholder="Prefix (e.g., math, phy)"
                value={uploadData.prefix}
                onChange={(e) => setUploadData({...uploadData, prefix: e.target.value})}
                required
              />
              <input
                type="file"
                accept=".js"
                onChange={(e) => setUploadData({...uploadData, server_file: e.target.files[0]})}
                required
              />
              <input
                type="file"
                onChange={(e) => setUploadData({...uploadData, folder: e.target.files[0]})}
              />
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowUpload(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">Upload</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="api-grid">
        {apis.map((api) => (
          <div key={api.id} className="api-card">
            <div className="api-header">
              <h3>{api.name}</h3>
              <span className="status-badge" style={{ backgroundColor: getStatusColor(api.status) }}>
                {api.status}
              </span>
            </div>
            <div className="api-info">
              <p><strong>Prefix:</strong> /{api.prefix}</p>
              <p><strong>Port:</strong> {api.port}</p>
              <p><strong>Routes:</strong> {api.routes?.length || 0}</p>
            </div>
            <div className="api-actions">
              {api.status === 'running' ? (
                <button className="btn-warning" onClick={() => handleStop(api.id)}>Stop</button>
              ) : (
                <button className="btn-success" onClick={() => handleStart(api.id)}>Start</button>
              )}
              <button className="btn-info" onClick={() => setSelectedApi(api)}>Details</button>
              <button className="btn-danger" onClick={() => handleDelete(api.id)}>Delete</button>
            </div>
          </div>
        ))}
      </div>

      {selectedApi && (
        <div className="modal-overlay">
          <div className="modal modal-large">
            <h2>{selectedApi.name} - Routes</h2>
            <div className="routes-list">
              {selectedApi.routes?.map((route) => (
                <div key={route.id} className="route-item">
                  <span className={`method method-${route.method.toLowerCase()}`}>{route.method}</span>
                  <span className="route-path">{route.path}</span>
                </div>
              ))}
            </div>
            <button className="btn-secondary" onClick={() => setSelectedApi(null)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}

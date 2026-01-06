import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [options, setOptions] = useState(null);
  const [formData, setFormData] = useState({
    paper_type: 'standard',
    paper_size: 'A4',
    color_type: 'bw',
    quantity: 100,
    sides: 'single',
    binding: 'none',
    lamination: 'none',
    turnaround: 'standard',
    additional_notes: ''
  });
  const [estimate, setEstimate] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    // Fetch available options
    fetch(`${API_URL}/options`)
      .then(res => res.json())
      .then(data => setOptions(data))
      .catch(err => console.error('Error fetching options:', err));
  }, [API_URL]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'quantity' ? parseInt(value) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setEstimate(null);

    try {
      const response = await fetch(`${API_URL}/estimate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error('Failed to calculate estimate');
      }

      const data = await response.json();
      setEstimate(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!options) {
    return <div className="loading">Loading options...</div>;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>🖨️ Print Job Price Calculator</h1>
        <p>Get instant AI-powered price estimates for your printing needs</p>
      </header>

      <div className="container">
        <form onSubmit={handleSubmit} className="calculator-form">
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="paper_type">Paper Type</label>
              <select
                id="paper_type"
                name="paper_type"
                value={formData.paper_type}
                onChange={handleInputChange}
              >
                {options.paper_types.map(type => (
                  <option key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="paper_size">Paper Size</label>
              <select
                id="paper_size"
                name="paper_size"
                value={formData.paper_size}
                onChange={handleInputChange}
              >
                {options.paper_sizes.map(size => (
                  <option key={size} value={size}>{size}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="color_type">Print Type</label>
              <select
                id="color_type"
                name="color_type"
                value={formData.color_type}
                onChange={handleInputChange}
              >
                <option value="bw">Black & White</option>
                <option value="color">Color</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="quantity">Quantity</label>
              <input
                type="number"
                id="quantity"
                name="quantity"
                min="1"
                value={formData.quantity}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="sides">Sides</label>
              <select
                id="sides"
                name="sides"
                value={formData.sides}
                onChange={handleInputChange}
              >
                <option value="single">Single-Sided</option>
                <option value="double">Double-Sided</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="binding">Binding</label>
              <select
                id="binding"
                name="binding"
                value={formData.binding}
                onChange={handleInputChange}
              >
                {options.binding_options.map(binding => (
                  <option key={binding} value={binding}>
                    {binding.charAt(0).toUpperCase() + binding.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="lamination">Lamination</label>
              <select
                id="lamination"
                name="lamination"
                value={formData.lamination}
                onChange={handleInputChange}
              >
                {options.lamination_options.map(lam => (
                  <option key={lam} value={lam}>
                    {lam.charAt(0).toUpperCase() + lam.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="turnaround">Turnaround Time</label>
              <select
                id="turnaround"
                name="turnaround"
                value={formData.turnaround}
                onChange={handleInputChange}
              >
                <option value="standard">Standard (5 days)</option>
                <option value="express">Express (2 days)</option>
                <option value="same_day">Same Day</option>
              </select>
            </div>
          </div>

          <div className="form-group full-width">
            <label htmlFor="additional_notes">Additional Notes (Optional)</label>
            <textarea
              id="additional_notes"
              name="additional_notes"
              value={formData.additional_notes}
              onChange={handleInputChange}
              rows="3"
              placeholder="Any special requirements or instructions..."
            />
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Calculating...' : 'Calculate Price'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {estimate && (
          <div className="estimate-result">
            <h2>Price Estimate</h2>
            
            <div className="price-highlight">
              <div className="total-price">
                <span className="label">Total Price</span>
                <span className="amount">${estimate.total_price.toFixed(2)}</span>
              </div>
              <div className="per-unit">
                ${estimate.breakdown.per_unit_cost.toFixed(2)} per unit
              </div>
            </div>

            <div className="price-breakdown">
              <h3>Price Breakdown</h3>
              <div className="breakdown-grid">
                <div className="breakdown-item">
                  <span>Base Price</span>
                  <span>${estimate.base_price.toFixed(2)}</span>
                </div>
                <div className="breakdown-item">
                  <span>Material Cost</span>
                  <span>${estimate.material_cost.toFixed(2)}</span>
                </div>
                <div className="breakdown-item">
                  <span>Labor Cost</span>
                  <span>${estimate.labor_cost.toFixed(2)}</span>
                </div>
                {estimate.breakdown.binding > 0 && (
                  <div className="breakdown-item">
                    <span>Binding</span>
                    <span>${estimate.breakdown.binding.toFixed(2)}</span>
                  </div>
                )}
                {estimate.breakdown.lamination > 0 && (
                  <div className="breakdown-item">
                    <span>Lamination</span>
                    <span>${estimate.breakdown.lamination.toFixed(2)}</span>
                  </div>
                )}
                {estimate.rush_fee > 0 && (
                  <div className="breakdown-item highlight">
                    <span>Rush Fee</span>
                    <span>${estimate.rush_fee.toFixed(2)}</span>
                  </div>
                )}
              </div>

              {estimate.breakdown.volume_discount_applied && (
                <div className="discount-badge">
                  ✓ Volume discount applied
                </div>
              )}
            </div>

            <div className="delivery-info">
              <strong>Estimated Delivery:</strong> {estimate.estimated_delivery}
            </div>

            <div className="confidence-badge">
              Confidence: {estimate.confidence}
            </div>
          </div>
        )}
      </div>

      <footer>
        <p>Powered by AI • Instant accurate quotes for your printing needs</p>
      </footer>
    </div>
  );
}

export default App;

import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [options, setOptions] = useState(null);
  const [formData, setFormData] = useState({
    product_type: 'label',
    material: 'polyester',
    size: '2x4',
    quantity: 100,
    colors: '1_color',
    finish: 'none',
    adhesive: 'standard',
    special_features: [],
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
    const { name, value, type, checked } = e.target;
    
    if (type === 'checkbox') {
      // Handle special_features checkboxes
      setFormData(prev => {
        const features = prev.special_features || [];
        if (checked) {
          return { ...prev, special_features: [...features, value] };
        } else {
          return { ...prev, special_features: features.filter(f => f !== value) };
        }
      });
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: name === 'quantity' ? parseInt(value) : value
      }));
    }
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
        <h1>🏭 NFI Corp - Price Calculator</h1>
        <p>Get instant AI-powered price estimates for industrial nameplates, labels & decals</p>
      </header>

      <div className="container">
        <form onSubmit={handleSubmit} className="calculator-form">
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="product_type">Product Type</label>
              <select
                id="product_type"
                name="product_type"
                value={formData.product_type}
                onChange={handleInputChange}
              >
                {options.product_types?.map(type => (
                  <option key={type} value={type}>
                    {type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="material">Material</label>
              <select
                id="material"
                name="material"
                value={formData.material}
                onChange={handleInputChange}
              >
                {options.materials?.map(material => (
                  <option key={material} value={material}>
                    {material === 'polyester' ? 'Polyester (PET/Mylar®)' :
                     material === 'polycarbonate' ? 'Polycarbonate (Lexan®)' :
                     material === 'stainless_steel' ? 'Stainless Steel' :
                     material.charAt(0).toUpperCase() + material.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="size">Size</label>
              <select
                id="size"
                name="size"
                value={formData.size}
                onChange={handleInputChange}
              >
                {options.sizes?.map(size => (
                  <option key={size} value={size}>
                    {size === 'custom' ? 'Custom Size' : `${size} inches`}
                  </option>
                ))}
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
              <label htmlFor="colors">Color Options</label>
              <select
                id="colors"
                name="colors"
                value={formData.colors}
                onChange={handleInputChange}
              >
                {options.colors?.map(color => (
                  <option key={color} value={color}>
                    {color === '1_color' ? '1 Color' :
                     color === '2_color' ? '2 Colors' :
                     'Full Color'}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="finish">Finish</label>
              <select
                id="finish"
                name="finish"
                value={formData.finish}
                onChange={handleInputChange}
              >
                {options.finishes?.map(finish => (
                  <option key={finish} value={finish}>
                    {finish === 'domed' ? 'Domed (Urethane)' :
                     finish.charAt(0).toUpperCase() + finish.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="adhesive">Adhesive</label>
              <select
                id="adhesive"
                name="adhesive"
                value={formData.adhesive}
                onChange={handleInputChange}
              >
                {options.adhesives?.map(adhesive => (
                  <option key={adhesive} value={adhesive}>
                    {adhesive.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
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
                <option value="standard">Standard (7-10 days)</option>
                <option value="rush">Rush (3-5 days)</option>
                <option value="express">Express (1-2 days)</option>
              </select>
            </div>
          </div>

          <div className="form-group full-width">
            <label>Special Features (Optional)</label>
            <div style={{display: 'flex', flexWrap: 'wrap', gap: '1rem', marginTop: '0.5rem'}}>
              {options.special_features?.map(feature => (
                <label key={feature} style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                  <input
                    type="checkbox"
                    name="special_features"
                    value={feature}
                    checked={formData.special_features?.includes(feature)}
                    onChange={handleInputChange}
                  />
                  {feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </label>
              ))}
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
                {estimate.breakdown.finish > 0 && (
                  <div className="breakdown-item">
                    <span>Finish</span>
                    <span>${estimate.breakdown.finish.toFixed(2)}</span>
                  </div>
                )}
                {estimate.breakdown.adhesive > 0 && (
                  <div className="breakdown-item">
                    <span>Adhesive</span>
                    <span>${estimate.breakdown.adhesive.toFixed(2)}</span>
                  </div>
                )}
                {estimate.breakdown.special_features > 0 && (
                  <div className="breakdown-item">
                    <span>Special Features</span>
                    <span>${estimate.breakdown.special_features.toFixed(2)}</span>
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
        <p>Powered by AI • Instant accurate quotes for industrial nameplates, labels & decals</p>
      </footer>
    </div>
  );
}

export default App;

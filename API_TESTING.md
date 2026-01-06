# API Testing Examples

Collection of curl commands to test your Printing Price Predictor API.

## Base URL

**Local**: `http://localhost:8000`
**Production**: `https://your-app.railway.app`

Replace `$API_URL` with your actual URL in the commands below.

---

## 1. Health Check

```bash
curl $API_URL/health
```

**Expected Response**:
```json
{"status": "healthy"}
```

---

## 2. Get Available Options

```bash
curl $API_URL/options
```

**Expected Response**:
```json
{
  "paper_types": ["standard", "glossy", "matte", "cardstock"],
  "paper_sizes": ["A4", "A3", "Letter", "Legal", "Custom"],
  "color_types": ["bw", "color"],
  "sides": ["single", "double"],
  "binding_options": ["none", "staple", "spiral", "perfect"],
  "lamination_options": ["none", "glossy", "matte"],
  "turnaround_options": ["standard", "express", "same_day"]
}
```

---

## 3. Calculate Price Estimate

### Example 1: Basic B&W Print Job

```bash
curl -X POST $API_URL/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "paper_type": "standard",
    "paper_size": "A4",
    "color_type": "bw",
    "quantity": 100,
    "sides": "single",
    "binding": "none",
    "lamination": "none",
    "turnaround": "standard"
  }'
```

### Example 2: Color Brochure with Binding

```bash
curl -X POST $API_URL/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "paper_type": "glossy",
    "paper_size": "A4",
    "color_type": "color",
    "quantity": 500,
    "sides": "double",
    "binding": "spiral",
    "lamination": "none",
    "turnaround": "standard"
  }'
```

### Example 3: Premium Business Cards

```bash
curl -X POST $API_URL/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "paper_type": "cardstock",
    "paper_size": "Custom",
    "color_type": "color",
    "quantity": 1000,
    "sides": "double",
    "binding": "none",
    "lamination": "glossy",
    "turnaround": "standard",
    "custom_width": 3.5,
    "custom_height": 2.0
  }'
```

### Example 4: Rush Order

```bash
curl -X POST $API_URL/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "paper_type": "matte",
    "paper_size": "Letter",
    "color_type": "color",
    "quantity": 50,
    "sides": "single",
    "binding": "staple",
    "lamination": "none",
    "turnaround": "same_day",
    "additional_notes": "Urgent presentation materials"
  }'
```

### Example 5: Large Volume Report

```bash
curl -X POST $API_URL/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "paper_type": "standard",
    "paper_size": "A4",
    "color_type": "bw",
    "quantity": 2000,
    "sides": "double",
    "binding": "perfect",
    "lamination": "none",
    "turnaround": "standard",
    "additional_notes": "Annual report - high volume discount expected"
  }'
```

---

## Expected Response Format

All estimate requests return:

```json
{
  "base_price": 50.00,
  "material_cost": 15.00,
  "labor_cost": 20.00,
  "rush_fee": 0.00,
  "total_price": 85.00,
  "breakdown": {
    "per_unit_cost": 0.85,
    "binding": 3.00,
    "lamination": 0.00,
    "volume_discount_applied": false,
    "reasoning": "Explanation of pricing (if AI-powered)"
  },
  "confidence": "High (Rule-based)" or "High/Medium/Low (AI)",
  "estimated_delivery": "2026-01-11"
}
```

---

## Testing with Python

```python
import requests

# Set your API URL
API_URL = "http://localhost:8000"  # or your Railway URL

# Test health check
response = requests.get(f"{API_URL}/health")
print("Health Check:", response.json())

# Get options
response = requests.get(f"{API_URL}/options")
print("Options:", response.json())

# Calculate estimate
job_data = {
    "paper_type": "glossy",
    "paper_size": "A4",
    "color_type": "color",
    "quantity": 500,
    "sides": "double",
    "binding": "spiral",
    "lamination": "none",
    "turnaround": "express"
}

response = requests.post(f"{API_URL}/estimate", json=job_data)
print("Estimate:", response.json())
```

---

## Testing with JavaScript/Node.js

```javascript
// Using fetch
const API_URL = "http://localhost:8000";

// Calculate estimate
async function getEstimate() {
  const response = await fetch(`${API_URL}/estimate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      paper_type: "glossy",
      paper_size: "A4",
      color_type: "color",
      quantity: 500,
      sides: "double",
      binding: "spiral",
      lamination: "none",
      turnaround: "standard"
    })
  });
  
  const data = await response.json();
  console.log('Estimate:', data);
}

getEstimate();
```

---

## Postman Collection

Import this JSON into Postman:

```json
{
  "info": {
    "name": "Printing Price Predictor API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": "{{base_url}}/health"
      }
    },
    {
      "name": "Get Options",
      "request": {
        "method": "GET",
        "header": [],
        "url": "{{base_url}}/options"
      }
    },
    {
      "name": "Calculate Estimate",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"paper_type\": \"glossy\",\n  \"paper_size\": \"A4\",\n  \"color_type\": \"color\",\n  \"quantity\": 500,\n  \"sides\": \"double\",\n  \"binding\": \"spiral\",\n  \"lamination\": \"none\",\n  \"turnaround\": \"standard\"\n}"
        },
        "url": "{{base_url}}/estimate"
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ]
}
```

---

## Load Testing (Optional)

Using Apache Bench:

```bash
# Test 100 requests with 10 concurrent
ab -n 100 -c 10 -p estimate.json -T application/json $API_URL/estimate
```

Create `estimate.json`:
```json
{
  "paper_type": "standard",
  "paper_size": "A4",
  "color_type": "bw",
  "quantity": 100,
  "sides": "single",
  "binding": "none",
  "lamination": "none",
  "turnaround": "standard"
}
```

---

## Error Scenarios

### Invalid Paper Type
```bash
curl -X POST $API_URL/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "paper_type": "invalid_type",
    "paper_size": "A4",
    "color_type": "bw",
    "quantity": 100,
    "sides": "single",
    "turnaround": "standard"
  }'
```

### Missing Required Fields
```bash
curl -X POST $API_URL/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "paper_type": "standard",
    "quantity": 100
  }'
```

---

Happy Testing! 🧪

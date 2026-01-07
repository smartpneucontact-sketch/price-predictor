from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import anthropic
import os
from datetime import datetime

app = FastAPI(title="Printing Price Predictor API")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class PrintJob(BaseModel):
    product_type: str  # "label", "nameplate", "decal", "asset_tag", "barcode_label"
    material: str  # "polyester", "polycarbonate", "vinyl", "aluminum", "stainless_steel"
    size: str  # "1x1", "2x4", "3x5", "4x6", "custom"
    quantity: int
    colors: str  # "1_color", "2_color", "full_color"
    finish: Optional[str] = None  # "matte", "gloss", "textured", "domed"
    adhesive: Optional[str] = None  # "standard", "high_tack", "removable", "none"
    special_features: Optional[list] = None  # ["barcode", "serial_number", "qr_code", "ul_certified"]
    turnaround: str  # "standard", "rush", "express"
    custom_width: Optional[float] = None
    custom_height: Optional[float] = None
    additional_notes: Optional[str] = None

class PriceEstimate(BaseModel):
    base_price: float
    material_cost: float
    labor_cost: float
    rush_fee: float
    total_price: float
    breakdown: dict
    confidence: str
    estimated_delivery: str

# Base pricing rules (fallback if AI is unavailable)
BASE_PRICES = {
    "material": {
        "polyester": 0.25,  # PET/Mylar
        "polycarbonate": 0.35,  # Lexan - durable
        "vinyl": 0.15,  # Standard vinyl
        "aluminum": 0.85,  # Metal nameplate
        "stainless_steel": 1.50  # Premium metal
    },
    "size_multiplier": {
        "1x1": 1.0,
        "2x2": 1.5,
        "2x4": 2.0,
        "3x5": 2.5,
        "4x6": 3.0,
        "custom": 2.0
    },
    "colors_multiplier": {
        "1_color": 1.0,
        "2_color": 1.3,
        "full_color": 1.8
    },
    "finish_cost": {
        "none": 0,
        "matte": 0.10,
        "gloss": 0.10,
        "textured": 0.25,
        "domed": 0.75  # Urethane doming
    },
    "adhesive_cost": {
        "none": 0,
        "standard": 0.05,
        "high_tack": 0.15,
        "removable": 0.10
    },
    "special_features_cost": {
        "barcode": 0.10,
        "serial_number": 0.15,
        "qr_code": 0.10,
        "ul_certified": 0.50,  # UL/CSA certification
        "rfid": 2.00
    },
    "turnaround_multiplier": {
        "standard": 1.0,  # 7-10 days
        "rush": 1.4,  # 3-5 days
        "express": 1.8  # 1-2 days
    }
}

def calculate_rule_based_price(job: PrintJob) -> PriceEstimate:
    """Fallback rule-based pricing calculation for nameplates/labels"""
    # Base per-unit cost
    base_per_unit = BASE_PRICES["material"].get(job.material, 0.25)
    base_per_unit *= BASE_PRICES["size_multiplier"].get(job.size, 1.0)
    base_per_unit *= BASE_PRICES["colors_multiplier"].get(job.colors, 1.0)
    
    # Calculate base price
    base_price = base_per_unit * job.quantity
    
    # Volume discounts for industrial orders
    if job.quantity > 5000:
        base_price *= 0.80  # 20% discount
    elif job.quantity > 1000:
        base_price *= 0.85  # 15% discount
    elif job.quantity > 500:
        base_price *= 0.90  # 10% discount
    elif job.quantity > 100:
        base_price *= 0.95  # 5% discount
    
    # Finish cost
    finish_cost = BASE_PRICES["finish_cost"].get(job.finish or "none", 0) * job.quantity
    
    # Adhesive cost
    adhesive_cost = BASE_PRICES["adhesive_cost"].get(job.adhesive or "none", 0) * job.quantity
    
    # Special features cost
    special_features_cost = 0
    if job.special_features:
        for feature in job.special_features:
            special_features_cost += BASE_PRICES["special_features_cost"].get(feature, 0) * job.quantity
    
    # Rush fee
    turnaround_multiplier = BASE_PRICES["turnaround_multiplier"].get(job.turnaround, 1.0)
    rush_fee = base_price * (turnaround_multiplier - 1)
    
    # Calculate totals
    material_cost = base_price * 0.35
    labor_cost = base_price * 0.45
    
    total = base_price + finish_cost + adhesive_cost + special_features_cost + rush_fee
    
    # Estimated delivery
    delivery_days = {"standard": 10, "rush": 5, "express": 2}
    delivery_date = datetime.now()
    if job.turnaround in delivery_days:
        from datetime import timedelta
        delivery_date += timedelta(days=delivery_days[job.turnaround])
    
    return PriceEstimate(
        base_price=round(base_price, 2),
        material_cost=round(material_cost, 2),
        labor_cost=round(labor_cost, 2),
        rush_fee=round(rush_fee, 2),
        total_price=round(total, 2),
        breakdown={
            "per_unit_cost": round(total / job.quantity, 2),
            "finish": round(finish_cost, 2),
            "adhesive": round(adhesive_cost, 2),
            "special_features": round(special_features_cost, 2),
            "volume_discount_applied": job.quantity > 100
        },
        confidence="High (Rule-based)",
        estimated_delivery=delivery_date.strftime("%Y-%m-%d")
    )

async def calculate_ai_price(job: PrintJob) -> PriceEstimate:
    """Use Claude AI to calculate intelligent price estimate"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        # Fallback to rule-based if no API key
        return calculate_rule_based_price(job)
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""You are an expert pricing analyst for NFI Corp, a commercial nameplate and industrial label manufacturer. 
Analyze this order and provide a detailed price breakdown.

Order Details:
- Product Type: {job.product_type}
- Material: {job.material}
- Size: {job.size}
- Quantity: {job.quantity}
- Colors: {job.colors}
- Finish: {job.finish or 'none'}
- Adhesive: {job.adhesive or 'none'}
- Special Features: {job.special_features or 'none'}
- Turnaround: {job.turnaround}
- Additional Notes: {job.additional_notes or 'none'}

Base Pricing Guidelines:
- Polyester (PET/Mylar): $0.25/unit, Polycarbonate (Lexan): $0.35/unit, Vinyl: $0.15/unit
- Aluminum: $0.85/unit, Stainless Steel: $1.50/unit
- Full color printing: 1.8x base cost, 2-color: 1.3x, 1-color: 1.0x
- Volume discounts: 5% for 100+, 10% for 500+, 15% for 1000+, 20% for 5000+
- Domed finish (urethane): $0.75/unit, Standard finishes: $0.10/unit
- Special features: Barcode $0.10, Serial number $0.15, UL certified $0.50, RFID $2.00
- Rush fees: Standard (7-10 days) +0%, Rush (3-5 days) +40%, Express (1-2 days) +80%

Provide a JSON response with this exact structure:
{{
    "base_price": <number>,
    "material_cost": <number>,
    "labor_cost": <number>,
    "rush_fee": <number>,
    "total_price": <number>,
    "breakdown": {{
        "per_unit_cost": <number>,
        "finish": <number>,
        "adhesive": <number>,
        "special_features": <number>,
        "volume_discount_applied": <boolean>,
        "reasoning": "<brief explanation>"
    }},
    "confidence": "<High/Medium/Low>",
    "estimated_delivery": "<YYYY-MM-DD>"
}}

Consider market rates for industrial nameplates, durability requirements, and provide competitive but profitable pricing."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse AI response
        import json
        response_text = message.content[0].text
        
        # Extract JSON from response (in case there's additional text)
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        json_str = response_text[json_start:json_end]
        
        ai_estimate = json.loads(json_str)
        
        return PriceEstimate(**ai_estimate)
        
    except Exception as e:
        print(f"AI pricing failed: {str(e)}, falling back to rule-based")
        return calculate_rule_based_price(job)

@app.get("/")
async def root():
    return {
        "service": "Printing Price Predictor API",
        "version": "1.0",
        "status": "operational"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/estimate", response_model=PriceEstimate)
async def estimate_price(job: PrintJob):
    """Calculate price estimate for a print job using AI"""
    try:
        estimate = await calculate_ai_price(job)
        return estimate
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating price: {str(e)}")

@app.get("/options")
async def get_options():
    """Get available options for the nameplate/label order form"""
    return {
        "product_types": ["label", "nameplate", "decal", "asset_tag", "barcode_label", "safety_label", "ul_label"],
        "materials": ["polyester", "polycarbonate", "vinyl", "aluminum", "stainless_steel"],
        "sizes": ["1x1", "2x2", "2x4", "3x5", "4x6", "custom"],
        "colors": ["1_color", "2_color", "full_color"],
        "finishes": ["none", "matte", "gloss", "textured", "domed"],
        "adhesives": ["none", "standard", "high_tack", "removable"],
        "special_features": ["barcode", "serial_number", "qr_code", "ul_certified", "rfid"],
        "turnaround_options": ["standard", "rush", "express"]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

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
    paper_type: str  # "standard", "glossy", "matte", "cardstock"
    paper_size: str  # "A4", "A3", "Letter", "Legal", "Custom"
    color_type: str  # "bw", "color"
    quantity: int
    sides: str  # "single", "double"
    binding: Optional[str] = None  # "none", "staple", "spiral", "perfect"
    lamination: Optional[str] = None  # "none", "glossy", "matte"
    turnaround: str  # "standard", "express", "same_day"
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
    "paper_type": {
        "standard": 0.05,
        "glossy": 0.12,
        "matte": 0.10,
        "cardstock": 0.20
    },
    "paper_size_multiplier": {
        "A4": 1.0,
        "Letter": 1.0,
        "A3": 1.8,
        "Legal": 1.2,
        "Custom": 1.5
    },
    "color_multiplier": {
        "bw": 1.0,
        "color": 2.5
    },
    "sides_multiplier": {
        "single": 1.0,
        "double": 1.6
    },
    "binding_cost": {
        "none": 0,
        "staple": 0.50,
        "spiral": 3.00,
        "perfect": 5.00
    },
    "lamination_cost": {
        "none": 0,
        "glossy": 1.50,
        "matte": 1.50
    },
    "turnaround_multiplier": {
        "standard": 1.0,
        "express": 1.5,
        "same_day": 2.0
    }
}

def calculate_rule_based_price(job: PrintJob) -> PriceEstimate:
    """Fallback rule-based pricing calculation"""
    # Base per-sheet cost
    base_per_sheet = BASE_PRICES["paper_type"].get(job.paper_type, 0.05)
    base_per_sheet *= BASE_PRICES["paper_size_multiplier"].get(job.paper_size, 1.0)
    base_per_sheet *= BASE_PRICES["color_multiplier"].get(job.color_type, 1.0)
    base_per_sheet *= BASE_PRICES["sides_multiplier"].get(job.sides, 1.0)
    
    # Calculate base price
    base_price = base_per_sheet * job.quantity
    
    # Volume discounts
    if job.quantity > 1000:
        base_price *= 0.85
    elif job.quantity > 500:
        base_price *= 0.90
    elif job.quantity > 100:
        base_price *= 0.95
    
    # Additional costs
    binding_cost = BASE_PRICES["binding_cost"].get(job.binding or "none", 0)
    lamination_cost = BASE_PRICES["lamination_cost"].get(job.lamination or "none", 0) * job.quantity
    
    # Rush fee
    turnaround_multiplier = BASE_PRICES["turnaround_multiplier"].get(job.turnaround, 1.0)
    rush_fee = base_price * (turnaround_multiplier - 1)
    
    # Calculate totals
    material_cost = base_price * 0.3
    labor_cost = base_price * 0.4 + binding_cost
    
    total = base_price + binding_cost + lamination_cost + rush_fee
    
    # Estimated delivery
    delivery_days = {"standard": 5, "express": 2, "same_day": 0}
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
            "binding": round(binding_cost, 2),
            "lamination": round(lamination_cost, 2),
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
        
        prompt = f"""You are an expert pricing analyst for a commercial printing company. 
Analyze this print job and provide a detailed price breakdown.

Job Details:
- Paper Type: {job.paper_type}
- Paper Size: {job.paper_size}
- Color: {job.color_type}
- Quantity: {job.quantity}
- Sides: {job.sides}
- Binding: {job.binding or 'none'}
- Lamination: {job.lamination or 'none'}
- Turnaround: {job.turnaround}
- Additional Notes: {job.additional_notes or 'none'}

Base Pricing Guidelines:
- Standard paper: $0.05/sheet, Glossy: $0.12/sheet, Matte: $0.10/sheet, Cardstock: $0.20/sheet
- Color printing costs 2.5x more than B&W
- Double-sided adds 60% to cost
- Volume discounts: 5% for 100+, 10% for 500+, 15% for 1000+
- Binding: Staple $0.50, Spiral $3.00, Perfect $5.00 per job
- Lamination: $1.50 per sheet
- Rush fees: Express +50%, Same day +100%

Provide a JSON response with this exact structure:
{{
    "base_price": <number>,
    "material_cost": <number>,
    "labor_cost": <number>,
    "rush_fee": <number>,
    "total_price": <number>,
    "breakdown": {{
        "per_unit_cost": <number>,
        "binding": <number>,
        "lamination": <number>,
        "volume_discount_applied": <boolean>,
        "reasoning": "<brief explanation>"
    }},
    "confidence": "<High/Medium/Low>",
    "estimated_delivery": "<YYYY-MM-DD>"
}}

Consider market rates, complexity, and provide competitive but profitable pricing."""

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
    """Get available options for the print job form"""
    return {
        "paper_types": ["standard", "glossy", "matte", "cardstock"],
        "paper_sizes": ["A4", "A3", "Letter", "Legal", "Custom"],
        "color_types": ["bw", "color"],
        "sides": ["single", "double"],
        "binding_options": ["none", "staple", "spiral", "perfect"],
        "lamination_options": ["none", "glossy", "matte"],
        "turnaround_options": ["standard", "express", "same_day"]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

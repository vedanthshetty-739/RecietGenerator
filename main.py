from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from typing import List
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

class ItemData(BaseModel):
    item_name: str
    quantity: float
    rate: float
    amount: float
    imei1:str = None
    imei2:str = None
    base_amount: float= 0.0

class ReceiptData(BaseModel):
    customer_name: str
    cgst: float
    sgst: float
    items: List[ItemData]
    cash: bool
    loan: bool
    total_amount: float

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate-receipt-pdf/")
async def create_receipt_pdf(request: Request, receipt_data: ReceiptData):
    # Calculate tax amounts (CGST and SGST at 9% each)
    total_amount = receipt_data.total_amount
    cgst_rate = receipt_data.cgst/100
    sgst_rate = receipt_data.sgst/100

    # Calculate base amount and taxes
    total_tax_rate = cgst_rate + sgst_rate
    base_amount = total_amount / (1 + total_tax_rate)
    cgst_amount = base_amount * cgst_rate
    sgst_amount = base_amount * sgst_rate

    # Calculate base amount for each item
    items_details = []
    for item in receipt_data.items:
        item_base_amount = item.amount / (1 + total_tax_rate)
        items_details.append({
            "item_name": item.item_name,
            "quantity": item.quantity,
            "imei1": item.imei1,
            "imei2": item.imei2,
            "rate": item.rate,
            "amount": f"{item.amount:.2f}",
            "base_amount": f"{item_base_amount:.2f}",
        })

    # Prepare template context
    receipt_context = {
        "request": request,
        "customer_name": receipt_data.customer_name,
        "receipt_no": datetime.now().strftime("%Y%m%d%H%M%S"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "items": items_details,
        "base_amount": f"{base_amount:.2f}",
        "cgst_percent": receipt_data.cgst,
        "sgst_percent": receipt_data.sgst,
        "cash": receipt_data.cash,
        "loan": receipt_data.loan,
        "cgst": f"{cgst_amount:.2f}",
        "sgst": f"{sgst_amount:.2f}",
        "total_amount": f"{total_amount:.2f}"
    }
    
    template_loader = FileSystemLoader(searchpath="./templates/")
    template_env = Environment(loader=template_loader)
    template = template_env.get_template("receipt.html")
    output_text = template.render(**receipt_context)
    pdf_bytes = HTML(string=output_text).write_pdf() # Get PDF as bytes

    # Return PDF data as a streaming response
    headers = {
        "Content-Disposition": "inline; filename=receipt.pdf", # inline instead of attachment
        "Content-Type": "application/pdf"
    }

    def iterfile():
        yield pdf_bytes

    return StreamingResponse(content=iterfile(), headers=headers, media_type="application/pdf")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
from enum import Enum
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
from jinja2 import Environment, FileSystemLoader
from reciet_counter import get_next_receipt_number
from weasyprint import HTML
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
# added logger
logger = logging.getLogger(__name__)

app = FastAPI(debug=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="/mnt/d/RecietGenerator/static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

class FinanceCompany(str, Enum):
    TVS_CREDIT = "TVS CREDIT"
    BAJAJ_FINANCE = "BAJAJ INANCE"

class PaymentType(str, Enum):
    CASH = "cash"
    LOAN = "loan"
    EMI = "emi"

class ItemData(BaseModel):
    item_name: str
    quantity: float
    rate: float
    amount: float
    imei1: Optional[str] = None
    imei2: Optional[str] = None
    base_amount: float = 0.0

class ReceiptData(BaseModel):
    customer_name: str
    customer_address: str
    cgst: float
    sgst: float
    items: List[ItemData]
    payment_type: PaymentType
    down_payment: Optional[int] = 0
    finance_company: Optional[FinanceCompany] = None

    total_amount: float

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate-receipt-pdf/")
async def create_receipt_pdf(request: Request, receipt_data: ReceiptData):
    # Calculate tax amounts
    total_amount = receipt_data.total_amount
    cgst_rate = receipt_data.cgst / 100
    sgst_rate = receipt_data.sgst / 100
    total_tax_rate = cgst_rate + sgst_rate
    base_amount = total_amount / (1 + total_tax_rate)
    cgst_amount = total_amount * cgst_rate
    sgst_amount = total_amount * sgst_rate

    # Prepare item details with base amount
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
    receipt_no = get_next_receipt_number()
    receipt_context = {
        "request": request,
        "receipt_no": receipt_no,
        "customer_name": receipt_data.customer_name,
        "customer_address": receipt_data.customer_address,
        "date": datetime.now().strftime("%d/%m/%Y"),
        "items": items_details,
        "base_amount": f"{base_amount:.2f}",
        "cgst_percent": receipt_data.cgst,
        "sgst_percent": receipt_data.sgst,
        "payment_type": receipt_data.payment_type.value,
        "cgst": f"{cgst_amount:.2f}",
        "sgst": f"{sgst_amount:.2f}",
        "total_amount": f"{total_amount:.2f}",
        "down_payment": receipt_data.down_payment,
        "finance_company": receipt_data.finance_company.value if receipt_data.finance_company else None
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
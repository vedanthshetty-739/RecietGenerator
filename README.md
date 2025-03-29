# Receipt Generator API

A FastAPI-based receipt generator that creates downloadable PDF receipts with automatic tax calculations, matching the format of Kshipra Mobiles tax invoices.

## Features

- Generate receipts with item details and automatic tax calculations
- CGST and SGST calculations (9% each)
- PDF download functionality
- Professional receipt layout matching the original format
- Includes all business details and tax information
- Red-colored borders and headers
- Cash/Loan payment options

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the FastAPI server:
```bash
python main.py
```

The server will start at `http://localhost:8000`

## API Usage

### Generate Receipt

**Endpoint:** `POST /generate-receipt/`

**Request Body:**
```json
{
    "item_name": "Samsung Galaxy M31",
    "description": "6GB RAM, 128GB Storage",
    "quantity": 1,
    "rate": 15000.00,
    "total_amount": 15000.00
}
```

**Response:**
- A downloadable PDF file containing the generated receipt in the exact format of Kshipra Mobiles tax invoice

### Example Using cURL

```bash
curl -X POST "http://localhost:8000/generate-receipt/" \
     -H "Content-Type: application/json" \
     -d '{"item_name": "Samsung Galaxy M31", "description": "6GB RAM, 128GB Storage", "quantity": 1, "rate": 15000.00, "total_amount": 15000.00}' \
     --output receipt.pdf
```

### Example Tax Calculation

For a total amount of ₹15000:
- Base amount: ₹12605.04
- CGST (9%): ₹1134.45
- SGST (9%): ₹1134.45
- Total: ₹15000.00

## Receipt Format

The generated receipt includes:
- Company header with GSTN and contact details
- Invoice number and date
- Customer details section
- Detailed item table with S.No., Particulars, Qty, Rate, and Amount
- Tax calculations (CGST and SGST)
- Cash/Loan payment options
- Signature field

## API Documentation

Once the server is running, you can access:
- Interactive API documentation at `http://localhost:8000/docs`
- Alternative API documentation at `http://localhost:8000/redoc` 
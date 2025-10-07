from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from tax_engine import compute_tax
from ocr_parser import parse_form16
from chatbot import get_chat_response  # Stub import
from utils import encrypt_data  # Stub import
import os

app = FastAPI(title="Tax Assistant API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/form16")
async def upload_form16(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Assume image; for PDF, convert in prod
    data = await file.read()
    
    # Encrypt stub
    encrypted_data = encrypt_data(data)
    
    parsed_data = parse_form16(encrypted_data)
    tax_summary = compute_tax(parsed_data)
    
    # Chatbot suggestion stub
    suggestion = get_chat_response("Suggest deductions for gross salary " + str(parsed_data.get('gross_salary', 0)))
    
    return {
        "parsed_data": parsed_data,
        "tax_summary": tax_summary,
        "suggestion": suggestion
    }

@app.get("/")
def root():
    return {"message": "Tax Assistant Backend Ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

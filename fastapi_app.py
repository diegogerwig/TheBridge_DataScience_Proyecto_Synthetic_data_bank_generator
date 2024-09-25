from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import pandas as pd
from main import generate_banking_data
import uvicorn


app = FastAPI()

class BankingDataRequest(BaseModel):
    profile: str
    job_category: str
    years: int
    name: Optional[str] = None
    iban: Optional[str] = None

class Transaction(BaseModel):
    Date: datetime
    Type: str
    Category: str
    Amount: float
    Location: str
    Balance: float

class BankingDataResponse(BaseModel):
    data: List[Transaction]
    summary: dict

@app.post("/generate_banking_data", response_model=BankingDataResponse)
async def generate_data(request: BankingDataRequest):
    if request.profile not in ['SAVER', 'NEUTRAL', 'SPENDER', 'MIXED']:
        raise HTTPException(status_code=400, detail="Invalid profile")
    if request.job_category not in ['MANAGER', 'TECHNICIAN', 'WORKER']:
        raise HTTPException(status_code=400, detail="Invalid job category")
    if request.years < 1 or request.years > 5:
        raise HTTPException(status_code=400, detail="Years must be between 1 and 5")

    df = generate_banking_data(days=request.years * 365, profile=request.profile, job_category=request.job_category)
    
    summary = {
        "total_income": float(df[df['Amount'] > 0]['Amount'].sum()),
        "total_expenses": float(abs(df[df['Amount'] < 0]['Amount'].sum())),
        "number_of_transactions": len(df),
        "final_balance": float(df['Balance'].iloc[-1])
    }
    
    return BankingDataResponse(data=df.to_dict('records'), summary=summary)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

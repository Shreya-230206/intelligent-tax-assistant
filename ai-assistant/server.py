from fastapi import FastAPI
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7)

prompt = PromptTemplate(
    input_variables=["query"],
    template="You are a helpful tax assistant. User query: {query}. Provide step-by-step guidance on Indian income tax, deductions, and regimes."
)

chain = LLMChain(llm=llm, prompt=prompt)

@app.post("/chat")
async def chat(query: str):
    response = chain.run(query)
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

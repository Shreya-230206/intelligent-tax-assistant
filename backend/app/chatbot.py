def get_chat_response(query: str):
    requests.post('http://localhost:8001/chat', json={'query': query})
    if "deduction" in query.lower() or "savings" in query.lower():
        return "Consider 80C investments (up to ₹1.5L) for old regime savings."
    elif "regime" in query.lower():
        return "New regime has lower rates but fewer deductions—compare based on your savings."
    return "Upload your Form 16 for personalized advice."

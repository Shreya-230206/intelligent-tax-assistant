def compute_tax(data, deductions=0):
    gross = data.get('gross_salary', 0) - deductions  # Placeholder for deductions
    
    # Old Regime (simplified slabs)
    old_tax = 0
    if gross > 500000:
        old_tax = 12500 + 0.20 * (gross - 500000)
    elif gross > 250000:
        old_tax = 0.05 * (gross - 250000)
    
    # New Regime (simplified slabs, lower rates)
    new_tax = 0
    if gross > 500000:
        new_tax = 12500 + 0.10 * (gross - 500000)
    elif gross > 250000:
        new_tax = 0.05 * (gross - 250000)
    
    return {
        'old_regime': round(old_tax, 2),
        'new_regime': round(new_tax, 2),
        'recommended_regime': 'new' if new_tax < old_tax else 'old',
        'savings': abs(old_tax - new_tax)
    }

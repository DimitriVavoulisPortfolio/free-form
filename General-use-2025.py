"""
Federal and State Tax Calculator 2025
====================================
A comprehensive calculator for federal and state income taxes with support for:
- Federal income tax calculation with progressive brackets
- Federal payroll taxes (Social Security and Medicare)
- State income taxes (flat rate, progressive brackets, or no state tax)
- Both single and joint filing statuses
"""

# TAX CONSTANTS
# =============
# All tax rates, brackets, and other constants in one centralized location for easy maintenance
TAX_DATA = {
    "federal": {
        "single": {
            "standard_deduction": 15000,
            "brackets": [
                (0, 11925, 0.10),
                (11925, 48475, 0.12),
                (48475, 103350, 0.22),
                (103350, 197300, 0.24),
                (197300, 250525, 0.32),
                (250525, float('inf'), 0.35)
            ]
        },
        "joint": {
            "standard_deduction": 30000,
            "brackets": [
                (0, 23850, 0.10),
                (23850, 96950, 0.12),
                (96950, 206700, 0.22),
                (206700, 394600, 0.24),
                (394600, 501050, 0.32),
                (501050, float('inf'), 0.35)
            ]
        },
        "payroll": {
            "ss_cap": 176100,  # Social Security wage base limit
            "ss_rate": 0.062,  # 6.2%
            "medicare_rate": 0.0145  # 1.45%
        }
    },
    "states": {
        # No income tax states
        "no_tax_states": [
            "texas", "florida", "washington", "nevada", "alaska", 
            "wyoming", "south_dakota", "tennessee", "new_hampshire"
        ],
        
        # Flat tax states
        "michigan": {
            "type": "flat",
            "name": "Michigan",
            "rate": 0.0425,  # 4.25%
            "description": "Flat rate of 4.25%"
        },
        "pennsylvania": {
            "type": "flat",
            "name": "Pennsylvania",
            "rate": 0.0307,  # 3.07%
            "description": "Flat rate of 3.07%"
        },
        "pennsylvania-philadelphia": {
            "type": "composite",
            "name": "Pennsylvania - Philadelphia",
            "state_rate": 0.0307,  # 3.07% (PA)
            "local_rate": 0.0375,  # 3.75% (Philadelphia)
            "total_rate": 0.0682,  # 6.82% combined
            "description": "PA state tax (3.07%) + Philadelphia local tax (3.75%)"
        },
        "pennsylvania-pittsburgh": {
            "type": "composite",
            "name": "Pennsylvania - Pittsburgh",
            "state_rate": 0.0307,  # 3.07% (PA)
            "local_rate": 0.03,    # 3.00% (Pittsburgh)
            "total_rate": 0.0607,  # 6.07% combined
            "flat_fee": 52,
            "description": "PA state tax (3.07%) + Pittsburgh local tax (3%) + $52 fee"
        },
        
        # Progressive bracket states
        "minnesota": {
            "type": "bracket",
            "name": "Minnesota",
            "single": {
                "standard_deduction": 14950,
                "brackets": [
                    (0, 32570, 0.0535),
                    (32570, 106990, 0.068),
                    (106990, 198630, 0.0785),
                    (198630, float('inf'), 0.0985)
                ]
            },
            "joint": {
                "standard_deduction": 29900,
                "brackets": [
                    (0, 47620, 0.0535),
                    (47620, 189180, 0.068),
                    (189180, 330410, 0.0785),
                    (330410, float('inf'), 0.0985)
                ]
            },
            "description": "Progressive tax with brackets based on filing status"
        }
    }
}

# UTILITY FUNCTIONS
# =================

def calculate_bracket_tax(taxable_income, brackets):
    """
    Calculate tax based on progressive tax brackets.
    
    Args:
        taxable_income: Income after deductions
        brackets: List of (lower_limit, upper_limit, rate) tuples
    
    Returns:
        Dictionary with total tax and breakdown by bracket
    """
    total_tax = 0
    breakdown = []
    
    for lower, upper, rate in brackets:
        if taxable_income > lower:
            # Calculate income in this bracket
            income_in_bracket = min(taxable_income, upper) - lower
            tax_in_bracket = income_in_bracket * rate
            total_tax += tax_in_bracket
            
            # Store breakdown for reporting
            breakdown.append({
                "bracket": f"${lower:,.2f} - ${upper:,.2f}" if upper != float('inf') else f"Over ${lower:,.2f}",
                "rate": f"{rate*100:.2f}%",
                "income": income_in_bracket,
                "tax": tax_in_bracket
            })
            
            # Break if we're done
            if taxable_income <= upper:
                break
                
    return {
        "total": total_tax,
        "breakdown": breakdown
    }

def format_currency(amount):
    """Format a number as currency with commas and 2 decimal places"""
    return f"${amount:,.2f}"

def format_percent(rate):
    """Format a number as a percentage with 2 decimal places"""
    return f"{rate:.2f}%"

# TAX CALCULATION FUNCTIONS
# =========================

def calculate_federal_tax(income1, income2=0, filing_status="single"):
    """
    Calculate federal income tax and payroll taxes.
    
    Args:
        income1: Primary earner's income
        income2: Secondary earner's income (for joint filing)
        filing_status: 'single' or 'joint'
        
    Returns:
        Dictionary with tax calculations
    """
    # Get tax constants based on filing status
    if filing_status not in ["single", "joint"]:
        raise ValueError(f"Invalid filing status: {filing_status}")
        
    fed_data = TAX_DATA["federal"][filing_status]
    standard_deduction = fed_data["standard_deduction"]
    brackets = fed_data["brackets"]
    
    # Calculate total income
    total_income = income1 + income2
    
    # Calculate taxable income after standard deduction
    taxable_income = max(0, total_income - standard_deduction)
    
    # Calculate income tax using brackets
    income_tax_result = calculate_bracket_tax(taxable_income, brackets)
    income_tax = income_tax_result["total"]
    bracket_breakdown = income_tax_result["breakdown"]
    
    # Calculate payroll taxes (Social Security and Medicare)
    ss_cap = TAX_DATA["federal"]["payroll"]["ss_cap"]
    ss_rate = TAX_DATA["federal"]["payroll"]["ss_rate"]
    medicare_rate = TAX_DATA["federal"]["payroll"]["medicare_rate"]
    
    # Social Security (capped at wage base limit per person)
    ss_tax1 = min(income1, ss_cap) * ss_rate
    ss_tax2 = min(income2, ss_cap) * ss_rate
    ss_tax_total = ss_tax1 + ss_tax2
    
    # Medicare (no income cap)
    medicare_tax1 = income1 * medicare_rate
    medicare_tax2 = income2 * medicare_rate
    medicare_tax_total = medicare_tax1 + medicare_tax2
    
    # Total payroll tax
    payroll_tax = ss_tax_total + medicare_tax_total
    
    # Total federal tax
    total_federal_tax = income_tax + payroll_tax
    
    # Effective tax rate
    effective_rate = (total_federal_tax / total_income) * 100 if total_income > 0 else 0
    
    # Build the result dictionary
    result = {
        "filing_status": filing_status,
        "gross_income": total_income,
        "standard_deduction": standard_deduction,
        "taxable_income": taxable_income,
        "income_tax": income_tax,
        "bracket_breakdown": bracket_breakdown,
        "social_security": {
            "rate": ss_rate * 100,
            "cap": ss_cap,
            "tax": ss_tax_total
        },
        "medicare": {
            "rate": medicare_rate * 100,
            "tax": medicare_tax_total
        },
        "payroll_tax": payroll_tax,
        "total_tax": total_federal_tax,
        "effective_rate": effective_rate
    }
    
    # Add filing-specific details
    if filing_status == "joint":
        result.update({
            "income1": income1,
            "income2": income2,
            "social_security_tax1": ss_tax1,
            "social_security_tax2": ss_tax2,
            "medicare_tax1": medicare_tax1,
            "medicare_tax2": medicare_tax2
        })
    
    return result

def calculate_state_tax(income1, income2=0, filing_status="single", state_code=""):
    """
    Calculate state income tax based on the specified state.
    
    Args:
        income1: Primary earner's income
        income2: Secondary earner's income (for joint filing)
        filing_status: 'single' or 'joint'
        state_code: State identifier code
        
    Returns:
        Dictionary with state tax calculations
    """
    # Calculate total income
    total_income = income1 + income2
    
    # Handle no-tax states
    if state_code == "" or state_code.lower() in TAX_DATA["states"]["no_tax_states"]:
        return {
            "state": state_code.upper() if state_code else "No State Tax",
            "tax": 0,
            "effective_rate": 0,
            "description": "No state income tax"
        }
    
    # Get state tax data
    if state_code.lower() not in TAX_DATA["states"]:
        raise ValueError(f"Unsupported state: {state_code}")
        
    state_data = TAX_DATA["states"][state_code.lower()]
    state_name = state_data["name"]
    
    # Handle flat tax states
    if state_data["type"] == "flat":
        state_tax = total_income * state_data["rate"]
        
        # Add flat fee if applicable
        flat_fee = state_data.get("flat_fee", 0)
        total_state_tax = state_tax + flat_fee
        
        effective_rate = (total_state_tax / total_income) * 100 if total_income > 0 else 0
        
        return {
            "state": state_name,
            "type": "flat",
            "rate": state_data["rate"] * 100,
            "tax": total_state_tax,
            "flat_fee": flat_fee,
            "effective_rate": effective_rate,
            "description": state_data["description"]
        }
    
    # Handle composite tax states (state + local)
    elif state_data["type"] == "composite":
        state_portion = total_income * state_data["state_rate"]
        local_portion = total_income * state_data["local_rate"]
        
        # Add flat fee if applicable (e.g., Pittsburgh)
        flat_fee = state_data.get("flat_fee", 0)
        total_state_tax = state_portion + local_portion + flat_fee
        
        effective_rate = (total_state_tax / total_income) * 100 if total_income > 0 else 0
        
        return {
            "state": state_name,
            "type": "composite",
            "state_rate": state_data["state_rate"] * 100,
            "local_rate": state_data["local_rate"] * 100,
            "state_portion": state_portion,
            "local_portion": local_portion,
            "total_rate": state_data["total_rate"] * 100,
            "tax": total_state_tax,
            "flat_fee": flat_fee,
            "effective_rate": effective_rate,
            "description": state_data["description"]
        }
    
    # Handle bracket states
    elif state_data["type"] == "bracket":
        # Get filing status specific data
        filing_key = filing_status if filing_status in state_data else "single"
        filing_data = state_data[filing_key]
        
        # Apply standard deduction
        standard_deduction = filing_data["standard_deduction"]
        taxable_income = max(0, total_income - standard_deduction)
        
        # Calculate tax using brackets
        tax_result = calculate_bracket_tax(taxable_income, filing_data["brackets"])
        state_tax = tax_result["total"]
        bracket_breakdown = tax_result["breakdown"]
        
        effective_rate = (state_tax / total_income) * 100 if total_income > 0 else 0
        
        return {
            "state": state_name,
            "type": "bracket",
            "standard_deduction": standard_deduction,
            "taxable_income": taxable_income,
            "tax": state_tax,
            "bracket_breakdown": bracket_breakdown,
            "effective_rate": effective_rate,
            "description": state_data["description"]
        }
    
    # Unknown state tax type
    else:
        raise ValueError(f"Unknown state tax type: {state_data['type']}")

def calculate_total_tax(income1, income2=0, filing_status="single", state_code=""):
    """
    Calculate both federal and state taxes and provide a combined result.
    
    Args:
        income1: Primary earner's income
        income2: Secondary earner's income (for joint filing)
        filing_status: 'single' or 'joint'
        state_code: State identifier code
        
    Returns:
        Dictionary with combined tax calculations
    """
    # Calculate federal taxes
    federal = calculate_federal_tax(income1, income2, filing_status)
    
    # Calculate state taxes
    state = calculate_state_tax(income1, income2, filing_status, state_code)
    
    # Calculate combined totals
    total_tax = federal["total_tax"] + state["tax"]
    total_income = federal["gross_income"]
    take_home = total_income - total_tax
    effective_rate = (total_tax / total_income) * 100 if total_income > 0 else 0
    
    # Combine results
    return {
        "federal": federal,
        "state": state,
        "total_tax": total_tax,
        "total_income": total_income,
        "take_home": take_home,
        "effective_rate": effective_rate
    }

# USER INTERFACE FUNCTIONS
# ========================

def get_state_options():
    """Generate a list of available state options for the UI"""
    options = [("", "Federal Only (No State Tax)")]
    
    # Add no-tax states
    for state in TAX_DATA["states"]["no_tax_states"]:
        state_name = state.replace("_", " ").title()
        options.append((state, f"{state_name} (No State Tax)"))
    
    # Add states with income tax
    for code, data in TAX_DATA["states"].items():
        if code == "no_tax_states":  # Skip the list of no-tax states
            continue
            
        if data["type"] == "flat":
            rate_info = f"({data['rate']*100:.2f}%)"
            if "flat_fee" in data:
                rate_info = f"({data['rate']*100:.2f}% + ${data['flat_fee']})"
            options.append((code, f"{data['name']} {rate_info}"))
            
        elif data["type"] == "composite":
            # Add composite tax locations with combined rate
            rate_info = f"({data['total_rate']*100:.2f}%)"
            if "flat_fee" in data:
                rate_info = f"({data['total_rate']*100:.2f}% + ${data['flat_fee']})"
            options.append((code, f"{data['name']} {rate_info}"))
            
        elif data["type"] == "bracket":
            options.append((code, f"{data['name']} (Progressive)"))
    
    # Sort alphabetically by display name
    return sorted(options, key=lambda x: x[1])

def display_tax_report(tax_data):
    """Display a formatted tax report to the console"""
    width = 80
    federal = tax_data["federal"]
    state = tax_data["state"]
    
    # Header
    print("=" * width)
    print("2025 TAX CALCULATION REPORT".center(width))
    print("=" * width)
    
    # Filing Status and State
    filing_text = "MARRIED FILING JOINTLY" if federal["filing_status"] == "joint" else "SINGLE"
    print(f"Filing Status: {filing_text}")
    print(f"State: {state['state']}")
    print("-" * width)
    
    # Income Information
    if federal["filing_status"] == "joint":
        print(f"Primary Income: {format_currency(federal['income1'])}")
        print(f"Secondary Income: {format_currency(federal['income2'])}")
    print(f"Total Income: {format_currency(federal['gross_income'])}")
    print()
    
    # FEDERAL TAX SECTION
    print("FEDERAL TAX CALCULATION".center(width))
    print("=" * width)
    
    # Income Tax
    print("INCOME TAX:")
    print(f"Gross Income: {format_currency(federal['gross_income'])}")
    print(f"Standard Deduction: -{format_currency(federal['standard_deduction'])}")
    print(f"Taxable Income: {format_currency(federal['taxable_income'])}")
    print()
    
    # Bracket Breakdown
    print("TAX BRACKET BREAKDOWN:")
    print("-" * width)
    print(f"{'Bracket':<30} {'Rate':<10} {'Income in Bracket':<20} {'Tax':<15}")
    print("-" * width)
    
    for bracket in federal["bracket_breakdown"]:
        print(f"{bracket['bracket']:<30} {bracket['rate']:<10} " +
              f"{format_currency(bracket['income']):<20} {format_currency(bracket['tax']):<15}")
    
    print("-" * width)
    print(f"Total Federal Income Tax: {format_currency(federal['income_tax'])}")
    print()
    
    # Payroll Taxes
    print("PAYROLL TAXES:")
    print(f"Note: Social Security tax applies up to {format_currency(federal['social_security']['cap'])} per person")
    print("-" * width)
    
    # Fix the Medicare percentage display to exactly 1.45%
    ss_rate = federal['social_security']['rate']
    mc_rate = 1.45  # Fixed to exactly 1.45% instead of using the value from the dictionary
    
    if federal["filing_status"] == "joint":
        print(f"Primary Income: {format_currency(federal['income1'])}")
        print(f"  Social Security ({ss_rate:.2f}%): {format_currency(federal['social_security_tax1'])}")
        print(f"  Medicare ({mc_rate:.2f}%): {format_currency(federal['medicare_tax1'])}")
        
        print(f"Secondary Income: {format_currency(federal['income2'])}")
        print(f"  Social Security ({ss_rate:.2f}%): {format_currency(federal['social_security_tax2'])}")
        print(f"  Medicare ({mc_rate:.2f}%): {format_currency(federal['medicare_tax2'])}")
    else:
        print(f"Social Security ({ss_rate:.2f}%): {format_currency(federal['social_security']['tax'])}")
        print(f"Medicare ({mc_rate:.2f}%): {format_currency(federal['medicare']['tax'])}")
    
    print("-" * width)
    print(f"Total Payroll Tax: {format_currency(federal['payroll_tax'])}")
    print()
    
    # Federal Summary
    print("FEDERAL TAX SUMMARY:")
    print(f"Federal Income Tax: {format_currency(federal['income_tax'])}")
    print(f"Federal Payroll Tax: {format_currency(federal['payroll_tax'])}")
    print(f"Total Federal Tax: {format_currency(federal['total_tax'])}")
    print(f"Federal Effective Tax Rate: {format_percent(federal['effective_rate'])}")
    print()
    
    # STATE TAX SECTION
    print("STATE TAX CALCULATION".center(width))
    print("=" * width)
    
    if state["tax"] == 0:
        print("No state income tax applies.")
    else:
        print(f"State: {state['state']}")
        
        if state["type"] == "flat":
            print(f"Tax Type: Flat Rate")
            print(f"Flat Tax Rate: {format_percent(state['rate'])}")
            print(f"Gross Income: {format_currency(federal['gross_income'])}")
            
            if state.get("flat_fee", 0) > 0:
                print(f"Additional Fee: {format_currency(state['flat_fee'])}")
                
            print(f"Total State Tax: {format_currency(state['tax'])}")
            
        elif state["type"] == "composite":
            print(f"Tax Type: Composite (State + Local)")
            print(f"Gross Income: {format_currency(federal['gross_income'])}")
            print()
            print(f"State Tax Rate: {format_percent(state['state_rate'])}")
            print(f"State Tax Portion: {format_currency(state['state_portion'])}")
            print()
            print(f"Local Tax Rate: {format_percent(state['local_rate'])}")
            print(f"Local Tax Portion: {format_currency(state['local_portion'])}")
            
            if state.get("flat_fee", 0) > 0:
                print(f"Additional Fee: {format_currency(state['flat_fee'])}")
            
            print("-" * width)
            print(f"Combined Tax Rate: {format_percent(state['total_rate'])}")
            print(f"Total State Tax: {format_currency(state['tax'])}")
            
        elif state["type"] == "bracket":
            print(f"Tax Type: Progressive Brackets")
            print(f"Gross Income: {format_currency(federal['gross_income'])}")
            print(f"Standard Deduction: -{format_currency(state['standard_deduction'])}")
            print(f"Taxable Income: {format_currency(state['taxable_income'])}")
            print()
            
            # State Bracket Breakdown
            print("STATE TAX BRACKET BREAKDOWN:")
            print("-" * width)
            print(f"{'Bracket':<30} {'Rate':<10} {'Income in Bracket':<20} {'Tax':<15}")
            print("-" * width)
            
            for bracket in state["bracket_breakdown"]:
                print(f"{bracket['bracket']:<30} {bracket['rate']:<10} " +
                      f"{format_currency(bracket['income']):<20} {format_currency(bracket['tax']):<15}")
            
            print("-" * width)
            print(f"Total State Tax: {format_currency(state['tax'])}")
        
        print(f"State Effective Tax Rate: {format_percent(state['effective_rate'])}")
    
    print()
    
    # COMBINED SUMMARY
    print("COMBINED TAX SUMMARY".center(width))
    print("=" * width)
    print(f"Gross Income: {format_currency(tax_data['total_income'])}")
    print(f"Federal Tax: {format_currency(federal['total_tax'])}")
    print(f"State Tax: {format_currency(state['tax'])}")
    print(f"Total Tax: {format_currency(tax_data['total_tax'])}")
    print(f"Take Home Pay: {format_currency(tax_data['take_home'])}")
    print(f"Combined Effective Tax Rate: {format_percent(tax_data['effective_rate'])}")
    print("=" * width)

def run_tax_calculator():
    """Run the interactive tax calculator program"""
    print("\n" + "=" * 80)
    print("2025 FEDERAL AND STATE TAX CALCULATOR".center(80))
    print("=" * 80)
    print("This calculator estimates federal income tax, payroll taxes, and state income taxes.")
    print(f"NOTE: Social Security tax has a cap of ${TAX_DATA['federal']['payroll']['ss_cap']:,.2f} per person.")
    
    while True:
        try:
            # Get state selection
            state_options = get_state_options()
            
            print("\nSelect a state or jurisdiction:")
            for i, (code, name) in enumerate(state_options, 1):
                print(f"{i}. {name}")
            print("q. Quit")
            
            choice = input("\nEnter your choice (number or q): ").lower()
            
            if choice == 'q':
                break
                
            try:
                index = int(choice) - 1
                if index < 0 or index >= len(state_options):
                    print("Invalid selection. Please try again.")
                    continue
                
                state_code = state_options[index][0]
            except ValueError:
                print("Invalid input. Please enter a number or 'q'.")
                continue
            
            # Get filing status
            print("\nSelect filing status:")
            print("1. Single")
            print("2. Married Filing Jointly")
            
            status_choice = input("Enter your choice (1/2): ")
            
            if status_choice == '1':
                filing_status = "single"
                income1 = float(input("Enter your income: $"))
                income2 = 0
            elif status_choice == '2':
                filing_status = "joint"
                income1 = float(input("Enter primary income: $"))
                income2 = float(input("Enter secondary income: $"))
            else:
                print("Invalid selection. Please try again.")
                continue
            
            # Validate incomes
            if income1 < 0 or income2 < 0:
                print("Income cannot be negative. Please try again.")
                continue
            
            # Calculate and display taxes
            tax_results = calculate_total_tax(income1, income2, filing_status, state_code)
            display_tax_report(tax_results)
            
            # Ask if user wants to do another calculation
            again = input("\nCalculate another scenario? (y/n): ").lower()
            if again != 'y':
                break
                
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    print("\nThank you for using the 2025 Tax Calculator!")

# Run the program if executed directly
if __name__ == "__main__":
    run_tax_calculator()
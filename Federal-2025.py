def calculate_taxes(income1, income2=0, filing_status="single"):
    """
    Calculate federal income tax and payroll taxes based on filing status.
    
    Args:
        income1: Primary income (required for all filing types)
        income2: Secondary income (used for joint filing, defaults to 0)
        filing_status: 'single' or 'joint'
    
    Returns:
        Dictionary containing tax calculation details
    """
    # Tax year 2025 constants - centralized for easy maintenance
    TAX_CONSTANTS = {
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
        }
    }
    
    # Payroll tax constants (same for all filing statuses)
    SS_CAP = 176100  # Social Security cap per person
    SS_RATE = 0.062  # 6.2%
    MC_RATE = 0.0145  # 1.45%
    
    # Get the appropriate constants based on filing status
    if filing_status not in TAX_CONSTANTS:
        raise ValueError(f"Invalid filing status: {filing_status}")
    
    STANDARD_DEDUCTION = TAX_CONSTANTS[filing_status]["standard_deduction"]
    brackets = TAX_CONSTANTS[filing_status]["brackets"]
    
    # Calculate total income based on filing status
    if filing_status == "single":
        total_income = income1
        income2 = 0  # Ensure income2 is 0 for single filers
    else:  # joint
        total_income = income1 + income2
    
    # Calculate taxable income (after standard deduction - ONLY FOR INCOME TAX)
    taxable_income = max(0, total_income - STANDARD_DEDUCTION)
    
    # Calculate income tax and track breakdown by bracket
    income_tax = 0
    bracket_breakdown = []
    
    for lower_limit, upper_limit, rate in brackets:
        if taxable_income > lower_limit:
            # Calculate tax for this bracket
            bracket_income = min(taxable_income, upper_limit) - lower_limit
            bracket_tax = bracket_income * rate
            income_tax += bracket_tax
            
            # Store breakdown information
            bracket_breakdown.append({
                "bracket": f"${lower_limit:,.2f} - ${upper_limit:,.2f}" if upper_limit != float('inf') else f"Over ${lower_limit:,.2f}",
                "rate": f"{rate*100:.1f}%",
                "income_in_bracket": bracket_income,
                "tax_for_bracket": bracket_tax
            })
            
            if taxable_income <= upper_limit:
                break
    
    # Calculate Social Security tax (capped at SS_CAP per person)
    ss_tax1 = min(income1, SS_CAP) * SS_RATE
    ss_tax2 = min(income2, SS_CAP) * SS_RATE if income2 > 0 else 0
    total_ss_tax = ss_tax1 + ss_tax2
    
    # Calculate Medicare tax (no income cap)
    mc_tax1 = income1 * MC_RATE
    mc_tax2 = income2 * MC_RATE if income2 > 0 else 0
    total_mc_tax = mc_tax1 + mc_tax2
    
    # Calculate total tax
    total_tax = income_tax + total_ss_tax + total_mc_tax
    
    # Calculate effective tax rate
    effective_rate = total_tax / total_income if total_income > 0 else 0
    
    # Build result dictionary based on filing status
    result = {
        "filing_status": filing_status,
        "gross_income": total_income,
        "standard_deduction": STANDARD_DEDUCTION,
        "taxable_income": taxable_income,
        "income_tax": income_tax,
        "social_security_tax": total_ss_tax,
        "medicare_tax": total_mc_tax,
        "total_tax": total_tax,
        "take_home_pay": total_income - total_tax,
        "effective_tax_rate": effective_rate * 100,  # as percentage
        "bracket_breakdown": bracket_breakdown
    }
    
    # Add spouse-specific information for joint filing
    if filing_status == "joint":
        result.update({
            "spouse1_income": income1,
            "spouse2_income": income2,
            "ss_tax_spouse1": ss_tax1,
            "ss_tax_spouse2": ss_tax2,
            "mc_tax_spouse1": mc_tax1,
            "mc_tax_spouse2": mc_tax2
        })
    else:
        result.update({
            "ss_tax_person": ss_tax1,
            "mc_tax_person": mc_tax1
        })
    
    return result

def display_tax_info(tax_info):
    """Display formatted tax calculation results for any filing status"""
    # Set display width based on filing status (joint needs more space)
    width = 80 if tax_info['filing_status'] == 'joint' else 70
    
    # Display header with appropriate filing status
    status_text = "MARRIED FILING JOINTLY" if tax_info['filing_status'] == 'joint' else "SINGLE"
    print("\n" + "="*width)
    print(f"2025 FEDERAL TAX CALCULATION - {status_text}")
    print("="*width)
    
    # Display income information based on filing status
    if tax_info['filing_status'] == 'joint':
        print(f"Spouse 1 Income: ${tax_info['spouse1_income']:,.2f}")
        print(f"Spouse 2 Income: ${tax_info['spouse2_income']:,.2f}")
        print(f"Total Household Income: ${tax_info['gross_income']:,.2f}")
    else:
        print(f"Gross Income: ${tax_info['gross_income']:,.2f}")
    
    # Income tax section
    print("\nFEDERAL INCOME TAX CALCULATION:")
    print(f"Gross Income: ${tax_info['gross_income']:,.2f}")
    print(f"Standard Deduction: -${tax_info['standard_deduction']:,.2f} (applies ONLY to income tax)")
    print(f"Taxable Income for Income Tax: ${tax_info['taxable_income']:,.2f}")
    print("-"*width)
    
    # Display income tax breakdown by bracket
    print("\nINCOME TAX BREAKDOWN BY BRACKET:")
    print("-"*width)
    bracket_col_width = 25 if tax_info['filing_status'] == 'joint' else 20
    print(f"{'Bracket':<{bracket_col_width}} {'Rate':<10} {'Amount in Bracket':<20} {'Tax':<15}")
    print("-"*width)
    
    for bracket in tax_info['bracket_breakdown']:
        print(f"{bracket['bracket']:<{bracket_col_width}} {bracket['rate']:<10} ${bracket['income_in_bracket']:,.2f}{' ':<10} ${bracket['tax_for_bracket']:,.2f}")
    
    print("-"*width)
    print(f"Total Income Tax: ${tax_info['income_tax']:,.2f}")
    
    # Display payroll taxes - emphasize they are on gross income
    print("\nPAYROLL TAXES (calculated on GROSS income, no standard deduction):")
    print("-"*width)
    
    # Display Social Security cap information
    print(f"Note: Social Security tax applies up to ${SS_CAP:,.2f} per person")
    print("-"*width)
    
    # Display payroll tax details based on filing status
    if tax_info['filing_status'] == 'joint':
        print(f"Spouse 1 Income: ${tax_info['spouse1_income']:,.2f}")
        print(f"  Social Security Tax (6.2% up to ${SS_CAP:,.2f}): ${tax_info['ss_tax_spouse1']:,.2f}")
        print(f"  Medicare Tax (1.45% on all income): ${tax_info['mc_tax_spouse1']:,.2f}")
        
        print(f"Spouse 2 Income: ${tax_info['spouse2_income']:,.2f}")
        print(f"  Social Security Tax (6.2% up to ${SS_CAP:,.2f}): ${tax_info['ss_tax_spouse2']:,.2f}")
        print(f"  Medicare Tax (1.45% on all income): ${tax_info['mc_tax_spouse2']:,.2f}")
    else:
        print(f"Gross Income for Payroll Taxes: ${tax_info['gross_income']:,.2f}")
        print(f"Social Security Tax (6.2% up to ${SS_CAP:,.2f}): ${tax_info['social_security_tax']:,.2f}")
        print(f"Medicare Tax (1.45% on all income): ${tax_info['medicare_tax']:,.2f}")
    
    print("-"*width)
    print(f"Total Social Security Tax: ${tax_info['social_security_tax']:,.2f}")
    print(f"Total Medicare Tax: ${tax_info['medicare_tax']:,.2f}")
    
    # Display summary
    print("\nSUMMARY:")
    print("-"*width)
    print(f"Income Tax: ${tax_info['income_tax']:,.2f}")
    print(f"Social Security Tax: ${tax_info['social_security_tax']:,.2f}")
    print(f"Medicare Tax: ${tax_info['medicare_tax']:,.2f}")
    print(f"Total Taxes: ${tax_info['total_tax']:,.2f}")
    print(f"Take Home Pay: ${tax_info['take_home_pay']:,.2f}")
    print(f"Effective Tax Rate: {tax_info['effective_tax_rate']:.2f}%")
    print("="*width)

# Constants defined at module level for display purposes
SS_CAP = 176100

# Example usage
if __name__ == "__main__":
    print("\n2025 FEDERAL TAX CALCULATOR")
    print("This calculator estimates federal income tax and payroll taxes.")
    print("NOTE: Standard deduction applies ONLY to income tax, NOT to payroll taxes.")
    print("NOTE: Social Security tax has a separate cap of $176,100 per person.")
    
    while True:
        try:
            print("\nSelect filing status:")
            print("1. Single")
            print("2. Married Filing Jointly")
            print("q. Quit")
            
            selection = input("Enter your choice (1/2/q): ").lower()
            
            if selection == 'q':
                break
            
            if selection == '1':
                filing_status = "single"
                income1 = float(input("Enter your income: $"))
                if income1 < 0:
                    print("Income cannot be negative. Please try again.")
                    continue
                tax_info = calculate_taxes(income1, filing_status=filing_status)
                
            elif selection == '2':
                filing_status = "joint"
                income1 = float(input("Enter first spouse's income: $"))
                income2 = float(input("Enter second spouse's income: $"))
                if income1 < 0 or income2 < 0:
                    print("Income cannot be negative. Please try again.")
                    continue
                tax_info = calculate_taxes(income1, income2, filing_status=filing_status)
                
            else:
                print("Invalid selection. Please try again.")
                continue
                
            display_tax_info(tax_info)
            
        except ValueError:
            print("Invalid input. Please enter a valid number.")
        except Exception as e:
            print(f"An error occurred: {e}")
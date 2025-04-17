def calculate_taxes(income):
    # Constants
    STANDARD_DEDUCTION = 15000
    SS_CAP = 176100
    SS_RATE = 0.062  # 6.2%
    MC_RATE = 0.0145  # 1.45%
    
    # Income tax brackets
    brackets = [
        (0, 11925, 0.10),
        (11925, 48475, 0.12),
        (48475, 103350, 0.22),
        (103350, 197300, 0.24),
        (197300, 250525, 0.32),
        (250525, float('inf'), 0.35)
    ]
    
    # Calculate taxable income (after standard deduction - ONLY FOR INCOME TAX)
    taxable_income = max(0, income - STANDARD_DEDUCTION)
    
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
    
    # Calculate Social Security tax (capped at SS_CAP)
    # NOTE: Social Security tax is based on gross income (no standard deduction)
    ss_tax = min(income, SS_CAP) * SS_RATE
    
    # Calculate Medicare tax (no income cap)
    # NOTE: Medicare tax is based on gross income (no standard deduction)
    mc_tax = income * MC_RATE
    
    # Calculate total tax
    total_tax = income_tax + ss_tax + mc_tax
    
    # Calculate effective tax rate
    effective_rate = total_tax / income if income > 0 else 0
    
    return {
        "gross_income": income,
        "taxable_income": taxable_income,
        "income_tax": income_tax,
        "social_security_tax": ss_tax,
        "medicare_tax": mc_tax,
        "total_tax": total_tax,
        "take_home_pay": income - total_tax,
        "effective_tax_rate": effective_rate * 100,  # as percentage
        "bracket_breakdown": bracket_breakdown
    }

def display_tax_info(tax_info):
    print("\n" + "="*70)
    print(f"TAX CALCULATION RESULTS")
    print("="*70)
    print(f"Gross Income: ${tax_info['gross_income']:,.2f}")
    
    # Clearly indicate standard deduction only applies to income tax
    print("\nFEDERAL INCOME TAX CALCULATION:")
    print(f"Gross Income: ${tax_info['gross_income']:,.2f}")
    print(f"Standard Deduction: -${STANDARD_DEDUCTION:,.2f} (applies ONLY to income tax)")
    print(f"Taxable Income for Income Tax: ${tax_info['taxable_income']:,.2f}")
    print("-"*70)
    
    # Display income tax breakdown by bracket
    print("\nINCOME TAX BREAKDOWN BY BRACKET:")
    print("-"*70)
    print(f"{'Bracket':<20} {'Rate':<10} {'Amount in Bracket':<20} {'Tax':<15}")
    print("-"*70)
    
    for bracket in tax_info['bracket_breakdown']:
        print(f"{bracket['bracket']:<20} {bracket['rate']:<10} ${bracket['income_in_bracket']:,.2f}{' ':<10} ${bracket['tax_for_bracket']:,.2f}")
    
    print("-"*70)
    print(f"Total Income Tax: ${tax_info['income_tax']:,.2f}")
    
    # Display payroll taxes - emphasize they are on gross income
    print("\nPAYROLL TAXES (calculated on GROSS income, no standard deduction):")
    print("-"*70)
    print(f"Gross Income for Payroll Taxes: ${tax_info['gross_income']:,.2f}")
    print(f"Social Security Tax (6.2% up to ${SS_CAP:,.2f}): ${tax_info['social_security_tax']:,.2f}")
    print(f"Medicare Tax (1.45% on all income): ${tax_info['medicare_tax']:,.2f}")
    
    # Display summary
    print("\nSUMMARY:")
    print("-"*70)
    print(f"Income Tax: ${tax_info['income_tax']:,.2f}")
    print(f"Social Security Tax: ${tax_info['social_security_tax']:,.2f}")
    print(f"Medicare Tax: ${tax_info['medicare_tax']:,.2f}")
    print(f"Total Taxes: ${tax_info['total_tax']:,.2f}")
    print(f"Take Home Pay: ${tax_info['take_home_pay']:,.2f}")
    print(f"Effective Tax Rate: {tax_info['effective_tax_rate']:.2f}%")
    print("="*70)

# Constants defined at module level for display purposes
STANDARD_DEDUCTION = 15000
SS_CAP = 176100

# Example usage
if __name__ == "__main__":
    print("\nU.S. TAX CALCULATOR")
    print("This calculator estimates federal income tax and payroll taxes.")
    print("NOTE: Standard deduction of $15,000 applies ONLY to income tax, NOT to payroll taxes.")
    
    while True:
        try:
            income_input = input("\nEnter your annual income (or 'q' to quit): ")
            if income_input.lower() == 'q':
                break
                
            income = float(income_input)
            if income < 0:
                print("Income cannot be negative. Please try again.")
                continue
                
            tax_info = calculate_taxes(income)
            display_tax_info(tax_info)
            
        except ValueError:
            print("Invalid input. Please enter a valid number or 'q' to quit.")
        except Exception as e:
            print(f"An error occurred: {e}")
import requests # type: ignore
import json
import os
from datetime import datetime

# Access Token
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiJCWDU5OTIiLCJqdGkiOiI2OGE2OWRmMzRhODgyMTQ0YWNlM2NhNWIiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc1NTc0OTg3NSwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzU1ODEzNjAwfQ.pu1tdQ3C1JBTpp1K7kvbAuEKUM4K327EaFs-rCVX9MY"

def get_upstox_holdings():
    """
    Function to fetch holdings from Upstox account using the provided access token
    """
    # API endpoint for Upstox holdings
    url = "https://api.upstox.com/v2/portfolio/long-term-holdings"
    
    # Headers including the access token for authorization
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Make the API request
        response = requests.get(url, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            
            if "status" in data and data["status"] == "success" and "data" in data:
                holdings = data["data"]
                
                if not holdings:
                    print("No holdings found in your account.")
                    return None
                
                holdings_data = []
                total_investment = 0
                total_current_value = 0
                
                for holding in holdings:
                    symbol = holding.get("tradingsymbol", "N/A")
                    quantity = holding.get("quantity", 0)
                    avg_price = holding.get("average_price", 0)
                    ltp = holding.get("last_price", 0)
                    pnl = holding.get("pnl", 0)
                    company_name = holding.get("company_name", "N/A")
                    
                    current_value = quantity * ltp
                    investment_value = quantity * avg_price
                    pnl_percent = (pnl / investment_value) * 100 if investment_value != 0 else 0
                    
                    total_investment += investment_value
                    total_current_value += current_value
                    
                    holdings_data.append({
                        "symbol": symbol,
                        "company_name": company_name,
                        "quantity": quantity,
                        "avg_price": avg_price,
                        "ltp": ltp,
                        "current_value": current_value,
                        "investment_value": investment_value,
                        "pnl": pnl,
                        "pnl_percent": pnl_percent
                    })
                
                # Calculate summary data
                total_pnl = total_current_value - total_investment
                total_pnl_percent = (total_pnl / total_investment) * 100 if total_investment != 0 else 0
                
                summary_data = {
                    "total_investment": total_investment,
                    "total_current_value": total_current_value,
                    "total_pnl": total_pnl,
                    "total_pnl_percent": total_pnl_percent,
                    "holdings_count": len(holdings_data),
                    "report_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                return {
                    "holdings": holdings_data,
                    "summary": summary_data
                }
                
            else:
                print("No holdings data found in the response.")
                print("Response structure:", json.dumps(data, indent=2))
                return None
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON response")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def generate_report():
    # Get the holdings data
    holdings_data = get_upstox_holdings()
    
    if holdings_data is None:
        print("Failed to fetch holdings data. Cannot generate report.")
        return
    
    # Create the report directory if it doesn't exist
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report")
    os.makedirs(report_dir, exist_ok=True)
    
    # Save the holdings data as JSON for the report to use
    data_file_path = os.path.join(report_dir, "holdings_data.js")
    with open(data_file_path, 'w') as file:
        file.write(f"const holdingsData = {json.dumps(holdings_data, indent=2)};")
    
    print(f"Holdings data saved to {data_file_path}")
    print(f"Report files generated in {report_dir}")
    print(f"Open {os.path.join(report_dir, 'index.html')} in your browser to view the report")

if __name__ == "__main__":
    generate_report()
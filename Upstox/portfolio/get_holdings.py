import requests # type: ignore
import json
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
            
            # Print holdings data in a formatted way
            print(f"\n{'=' * 80}")
            print(f"UPSTOX HOLDINGS AS OF {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'=' * 80}")
            
            if "status" in data and data["status"] == "success" and "data" in data:
                holdings = data["data"]
                
                if not holdings:
                    print("No holdings found in your account.")
                    return
                
                # Print holdings in a tabular format
                print(f"{'SYMBOL':<15} {'QTY':<8} {'AVG PRICE':<12} {'LTP':<10} {'CURRENT VALUE':<15} {'P&L':<10} {'P&L %':<10}")
                print(f"{'-' * 80}")
                
                total_investment = 0
                total_current_value = 0
                
                for holding in holdings:
                    symbol = holding.get("tradingsymbol", "N/A")
                    quantity = holding.get("quantity", 0)
                    avg_price = holding.get("average_price", 0)
                    ltp = holding.get("last_price", 0)
                    pnl = holding.get("pnl", 0)
                    
                    current_value = quantity * ltp
                    investment_value = quantity * avg_price
                    pnl_percent = (pnl / investment_value) * 100 if investment_value != 0 else 0
                    
                    total_investment += investment_value
                    total_current_value += current_value
                    
                    print(f"{symbol:<15} {quantity:<8} {avg_price:<12.2f} {ltp:<10.2f} {current_value:<15.2f} {pnl:<10.2f} {pnl_percent:<10.2f}%")
                
                # Print summary
                print(f"{'-' * 80}")
                total_pnl = total_current_value - total_investment
                total_pnl_percent = (total_pnl / total_investment) * 100 if total_investment != 0 else 0
                print(f"TOTAL INVESTMENT: ₹{total_investment:.2f}")
                print(f"TOTAL CURRENT VALUE: ₹{total_current_value:.2f}")
                print(f"OVERALL P&L: ₹{total_pnl:.2f} ({total_pnl_percent:.2f}%)")
                
            else:
                print("No holdings data found in the response.")
                print("Response structure:", json.dumps(data, indent=2))
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except json.JSONDecodeError:
        print("Error decoding JSON response")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    get_upstox_holdings()
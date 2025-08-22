#!/usr/bin/env python3
"""
Create instrument mapping from NSE.json.gz file
"""
import os
import json
import gzip
from datetime import datetime

def create_mapping_files(source_file):
    """Create mapping files from NSE.json.gz data."""
    print(f"\nReading data from: {source_file}")
    
    try:
        # Read the gzipped JSON file
        with gzip.open(source_file, 'rt', encoding='utf-8') as f:
            instruments = json.load(f)
        
        print(f"Successfully loaded {len(instruments)} instruments")
        
        # Create maps directory if it doesn't exist
        maps_dir = os.path.join(os.path.dirname(__file__), 'maps')
        os.makedirs(maps_dir, exist_ok=True)
        
        # Filter and process instruments
        equity_instruments = []
        for instr in instruments:
            if instr.get('instrument_type') == 'EQ':
                processed_instr = {
                    'segment': 'NSE_EQ',
                    'name': instr.get('name', ''),
                    'exchange': 'NSE',
                    'isin': instr.get('isin', ''),
                    'instrument_type': 'EQ',
                    'instrument_key': f"NSE_EQ|{instr.get('isin', '')}",
                    'lot_size': int(instr.get('lot_size', 1)),
                    'freeze_quantity': float(instr.get('freeze_qty', 0)),
                    'exchange_token': str(instr.get('token', '')),
                    'tick_size': float(instr.get('tick_size', 0)),
                    'trading_symbol': instr.get('symbol', ''),
                    'short_name': instr.get('name', ''),
                    'security_type': 'NORMAL'
                }
                equity_instruments.append(processed_instr)
        
        print(f"Found {len(equity_instruments)} equity instruments")
        
        # Save full instrument details
        details_file = os.path.join(maps_dir, 'instrument_details.json')
        with open(details_file, 'w') as f:
            json.dump(equity_instruments, f, indent=2)
        print(f"\nSaved full instrument details to: {details_file}")
        
        # Create symbol to instrument key mapping
        symbol_map = {
            instr['trading_symbol']: {
                'instrument_key': instr['instrument_key'],
                'name': instr['name'],
                'isin': instr['isin']
            } for instr in equity_instruments
        }
        
        symbol_file = os.path.join(maps_dir, 'symbol_map.json')
        with open(symbol_file, 'w') as f:
            json.dump(symbol_map, f, indent=2)
        print(f"Saved symbol mapping to: {symbol_file}")
        
        # Create ISIN to details mapping
        isin_map = {
            instr['isin']: {
                'symbol': instr['trading_symbol'],
                'name': instr['name'],
                'instrument_key': instr['instrument_key']
            } for instr in equity_instruments
        }
        
        isin_file = os.path.join(maps_dir, 'isin_map.json')
        with open(isin_file, 'w') as f:
            json.dump(isin_map, f, indent=2)
        print(f"Saved ISIN mapping to: {isin_file}")
        
        # Print sample for verification
        print(f"\nSample instrument data:")
        if equity_instruments:
            print(json.dumps(equity_instruments[0], indent=2))
            
    except Exception as e:
        print(f"Error processing file: {e}")

def main():
    print(f"Starting Instrument Mapping at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Source file is in test_zone directory
    source_file = os.path.join(os.path.dirname(__file__), 'NSE.json.gz')
    
    if os.path.exists(source_file):
        create_mapping_files(source_file)
        print("\nMapping files created successfully!")
    else:
        print(f"\nError: Source file not found: {source_file}")

if __name__ == '__main__':
    main()
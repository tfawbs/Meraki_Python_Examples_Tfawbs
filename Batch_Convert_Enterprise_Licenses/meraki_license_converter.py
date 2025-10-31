#!/usr/bin/env python3
"""
Meraki License Converter Script

This script converts Meraki networks from Essentials to Advantage license tier
using the Meraki Dashboard API batch operation.

Author: Generated for EA License Change
Version: 1.0
"""

import csv
import json
import logging
import os
import sys
import time
from typing import List, Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class MerakiLicenseConverter:
    """Main class for handling Meraki license conversions."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.meraki.com/api/v1"):
        """
        Initialize the Meraki License Converter.
        
        Args:
            api_key: Meraki Dashboard API key
            base_url: Meraki API base URL (default: production API)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = self._create_session()
        
        # Setup logging
        self._setup_logging()
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers
        session.headers.update({
            'X-Cisco-Meraki-API-Key': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        return session
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('meraki_conversion.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def read_csv_file(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """
        Read network data from CSV file.
        
        Expected CSV format:
        network_id,product_type,feature_tier
        
        Args:
            csv_file_path: Path to the CSV file
            
        Returns:
            List of dictionaries containing network data
        """
        networks = []
        
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                    # Validate required fields
                    required_fields = ['network_id', 'product_type', 'feature_tier']
                    missing_fields = [field for field in required_fields if not row.get(field)]
                    
                    if missing_fields:
                        self.logger.warning(f"Row {row_num}: Missing fields {missing_fields}, skipping")
                        continue
                    
                    # Clean and validate data
                    network_id = row['network_id'].strip()
                    product_type = row['product_type'].strip().lower()
                    feature_tier = row['feature_tier'].strip().lower()
                    
                    # Validate product type
                    valid_product_types = ['wireless', 'switch', 'appliance', 'camera', 'sensor']
                    if product_type not in valid_product_types:
                        self.logger.warning(f"Row {row_num}: Invalid product_type '{product_type}', skipping")
                        continue
                    
                    # Validate feature tier
                    valid_feature_tiers = ['essentials', 'advantage', 'enterprise']
                    if feature_tier not in valid_feature_tiers:
                        self.logger.warning(f"Row {row_num}: Invalid feature_tier '{feature_tier}', skipping")
                        continue
                    
                    networks.append({
                        'network_id': network_id,
                        'product_type': product_type,
                        'feature_tier': feature_tier
                    })
                    
        except FileNotFoundError:
            self.logger.error(f"CSV file not found: {csv_file_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {e}")
            raise
            
        self.logger.info(f"Successfully loaded {len(networks)} networks from CSV")
        return networks
    
    def validate_networks(self, networks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate that networks exist and are accessible.
        
        Args:
            networks: List of network dictionaries
            
        Returns:
            List of validated networks
        """
        validated_networks = []
        
        for network in networks:
            network_id = network['network_id']
            
            try:
                # Get network details to validate it exists
                response = self.session.get(f"{self.base_url}/networks/{network_id}")
                
                if response.status_code == 200:
                    network_data = response.json()
                    self.logger.info(f"✓ Network {network_id} validated: {network_data.get('name', 'Unknown')}")
                    validated_networks.append(network)
                elif response.status_code == 404:
                    self.logger.warning(f"✗ Network {network_id} not found, skipping")
                else:
                    self.logger.warning(f"✗ Network {network_id} validation failed: {response.status_code}")
                    
            except Exception as e:
                self.logger.error(f"✗ Error validating network {network_id}: {e}")
                
        self.logger.info(f"Validated {len(validated_networks)} out of {len(networks)} networks")
        return validated_networks
    
    def create_batch_payload(self, networks: List[Dict[str, Any]], is_atomic: bool = True) -> Dict[str, Any]:
        """
        Create the batch operation payload.
        
        Groups multiple product types for the same network ID into a single item.
        
        Args:
            networks: List of validated networks
            is_atomic: Whether the operation should be atomic (all succeed or all fail)
            
        Returns:
            Batch operation payload dictionary
        """
        # Group networks by network_id to handle multiple product types per network
        networks_by_id = {}
        
        for network in networks:
            network_id = network['network_id']
            
            if network_id not in networks_by_id:
                networks_by_id[network_id] = {
                    "network": {
                        "id": network_id,
                        "productTypes": []
                    }
                }
            
            # Add product type to the network
            networks_by_id[network_id]["network"]["productTypes"].append({
                "productType": network['product_type'],
                "featureTier": network['feature_tier']
            })
        
        # Convert grouped networks to items list
        items = list(networks_by_id.values())
        
        # Log grouping information
        for network_id, item in networks_by_id.items():
            product_types = [pt['productType'] for pt in item['network']['productTypes']]
            self.logger.info(f"Network {network_id}: grouping {len(product_types)} product type(s): {', '.join(product_types)}")
        
        payload = {
            "items": items,
            "isAtomic": is_atomic
        }
        
        return payload
    
    def execute_batch_conversion(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the batch license conversion.
        
        Args:
            payload: Batch operation payload
            
        Returns:
            API response dictionary
        """
        url = f"{self.base_url}/administered/licensing/subscription/networks/featureTiers/batchUpdate"
        
        self.logger.info(f"Executing batch conversion for {len(payload['items'])} networks...")
        self.logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info("✓ Batch conversion completed successfully")
                return result
            else:
                self.logger.error(f"✗ Batch conversion failed: {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"✗ Request failed: {e}")
            raise
    
    def process_conversion(self, csv_file_path: str, validate_networks: bool = True, is_atomic: bool = True) -> bool:
        """
        Main method to process the license conversion.
        
        Args:
            csv_file_path: Path to CSV file with network data
            validate_networks: Whether to validate networks before conversion
            is_atomic: Whether the operation should be atomic
            
        Returns:
            True if conversion was successful, False otherwise
        """
        try:
            # Read CSV file
            self.logger.info("Reading network data from CSV file...")
            networks = self.read_csv_file(csv_file_path)
            
            if not networks:
                self.logger.error("No valid networks found in CSV file")
                return False
            
            # Validate networks if requested
            if validate_networks:
                self.logger.info("Validating networks...")
                networks = self.validate_networks(networks)
                
                if not networks:
                    self.logger.error("No valid networks found after validation")
                    return False
            
            # Create batch payload
            self.logger.info("Creating batch operation payload...")
            payload = self.create_batch_payload(networks, is_atomic)
            
            # Execute conversion
            self.logger.info("Executing batch conversion...")
            result = self.execute_batch_conversion(payload)
            
            # Log results
            self.logger.info("Conversion completed successfully!")
            self.logger.info(f"Result: {json.dumps(result, indent=2)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Conversion failed: {e}")
            return False


def main():
    """Main function to run the license converter."""
    
    # Configuration
    API_KEY = os.getenv('MERAKI_API_KEY')
    CSV_FILE = os.getenv('CSV_FILE_PATH', 'networks.csv')
    VALIDATE_NETWORKS = os.getenv('VALIDATE_NETWORKS', 'true').lower() == 'true'
    IS_ATOMIC = os.getenv('IS_ATOMIC', 'true').lower() == 'true'
    
    # Check for API key
    if not API_KEY:
        print("Error: MERAKI_API_KEY environment variable not set")
        print("Please set your Meraki API key:")
        print("export MERAKI_API_KEY='your_api_key_here'")
        sys.exit(1)
    
    # Check if CSV file exists
    if not os.path.exists(CSV_FILE):
        print(f"Error: CSV file not found: {CSV_FILE}")
        print("Please create a CSV file with the following format:")
        print("network_id,product_type,feature_tier")
        print("N_1234567890abcdef,wireless,advantage")
        sys.exit(1)
    
    # Create converter instance
    converter = MerakiLicenseConverter(API_KEY)
    
    # Process conversion
    print(f"Starting Meraki license conversion...")
    print(f"CSV file: {CSV_FILE}")
    print(f"Validate networks: {VALIDATE_NETWORKS}")
    print(f"Atomic operation: {IS_ATOMIC}")
    print("-" * 50)
    
    success = converter.process_conversion(
        csv_file_path=CSV_FILE,
        validate_networks=VALIDATE_NETWORKS,
        is_atomic=IS_ATOMIC
    )
    
    if success:
        print("\n✓ License conversion completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ License conversion failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

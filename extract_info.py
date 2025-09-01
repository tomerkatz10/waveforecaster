#!/usr/bin/env python3
"""
Marine Weather Data Extractor
Fetches marine weather data from Open-Meteo API for wave forecasting
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

import requests
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MarineWeatherExtractor:
    """Class to extract marine weather data from Open-Meteo API"""

    def __init__(self, latitude: float = 32.08, longitude: float = 34.77):
        """
        Initialize the extractor with coordinates
        
        Args:
            latitude (float): Latitude coordinate (default: 32.08)
            longitude (float): Longitude coordinate (default: 34.77)
        """
        self.latitude = latitude
        self.longitude = longitude
        self.base_url = "https://marine-api.open-meteo.com/v1/marine"
        self.session = requests.Session()

    def build_api_url(self, length: int = 7) -> str:
        """
        Build the API URL with parameters
        
        Args:
            length (int): Number of days to forecast (default: 7)
            
        Returns:
            str: Complete API URL
        """
        params = {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'hourly': 'wave_height,wave_direction,wind_wave_height,wind_wave_direction,swell_wave_height,swell_wave_direction,swell_wave_period',
            'length': length
        }

        # Build query string
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}?{query_string}"

    def fetch_marine_data(self, length: int = 7) -> Optional[Dict[str, Any]]:
        """
        Fetch marine weather data from the API
        
        Args:
            length (int): Number of days to forecast (default: 7)
            
        Returns:
            Optional[Dict[str, Any]]: API response data or None if failed
        """
        url = self.build_api_url(length)

        try:
            logger.info(f"Fetching marine data from: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Successfully fetched data for {length} days")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    def assess_wave_conditions(self, wave_height: float, swell_height: float, swell_period: float) -> str:
        """
        Assess wave conditions based on wave height, swell height, and swell period
        Optimized for Israeli Mediterranean coast conditions
        
        Args:
            wave_height (float): Total wave height in meters
            swell_height (float): Swell wave height in meters
            swell_period (float): Swell wave period in seconds
            
        Returns:
            str: Condition rating ('Good', 'OK', 'Bad')
        """
        if wave_height is None or swell_height is None or swell_period is None:
            return 'Unknown'
        
        # Israeli Mediterranean coast specific thresholds
        # Mediterranean waves are generally smaller and more manageable than ocean waves
        # Good conditions: moderate wave height, decent swell, reasonable period
        # OK conditions: acceptable for various skill levels
        # Bad conditions: only truly unsuitable conditions
        
        # Check for dangerous conditions first (less aggressive)
        if wave_height > 4.0:  # Very high waves - dangerous (increased from 4.0m)
            return 'Bad'
        elif wave_height < 0.2:  # Too small to surf (decreased from 0.3m)
            return 'Bad'
        
        # Assess swell quality (balanced approach)
        if swell_height < 0.4:  # Poor swell (reduced from 0.5m)
            return 'Bad'
        elif swell_period < 5.0:  # Poor swell period (reduced from 5.5s)
            return 'Bad'
        
        # Good conditions: ideal for Israeli Mediterranean (selective)
        if (1.0 <= wave_height <= 3.2 and 
            0.8 <= swell_height <= 3.2 and 
            7.5 <= swell_period <= 15.0):
            return 'Good'
        
        # OK conditions: acceptable ranges (balanced)
        elif (0.5 <= wave_height <= 4.0 and 
              0.4 <= swell_height <= 3.8 and 
              5.0 <= swell_period <= 18.0):
            return 'OK'
        
        # Everything else is bad (much less aggressive)
        else:
            return 'Bad'

    def process_wave_data(self, data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Process and structure the wave data
        
        Args:
            data (Dict[str, Any]): Raw API response data
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Processed wave data organized by date
        """
        if not data or 'hourly' not in data:
            logger.error("Invalid data structure received")
            return {}

        hourly_data = data['hourly']
        processed_data = {}

        try:
            # Get the time array
            times = hourly_data.get('time', [])

            # Process each data point
            for i, timestamp in enumerate(times):
                date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                date_key = date.strftime('%Y-%m-%d')

                if date_key not in processed_data:
                    processed_data[date_key] = []

                # Extract wave parameters
                wave_height = hourly_data.get('wave_height', [None])[i]
                swell_height = hourly_data.get('swell_wave_height', [None])[i]
                swell_period = hourly_data.get('swell_wave_period', [None])[i]
                
                # Assess wave conditions
                wave_condition = self.assess_wave_conditions(wave_height, swell_height, swell_period)
                
                wave_data = {
                    'timestamp': timestamp,
                    'hour': date.hour,
                    'wave_height': wave_height,
                    'wave_direction': hourly_data.get('wave_direction', [None])[i],
                    'wind_wave_height': hourly_data.get('wind_wave_height', [None])[i],
                    'wind_wave_direction': hourly_data.get('wind_wave_direction', [None])[i],
                    'swell_wave_height': swell_height,
                    'swell_wave_direction': hourly_data.get('swell_wave_direction', [None])[i],
                    'swell_wave_period': swell_period,
                    'wave_condition': wave_condition
                }

                processed_data[date_key].append(wave_data)

            logger.info(f"Processed data for {len(processed_data)} days")
            return processed_data

        except Exception as e:
            logger.error(f"Error processing wave data: {e}")
            return {}

    def get_daily_summary(self, processed_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
        """
        Generate daily summary statistics
        
        Args:
            processed_data (Dict[str, List[Dict[str, Any]]]): Processed wave data
            
        Returns:
            Dict[str, Dict[str, Any]]: Daily summary statistics
        """
        daily_summary = {}

        for date, hourly_data in processed_data.items():
            if not hourly_data:
                continue

            # Calculate daily statistics
            wave_heights = [d['wave_height'] for d in hourly_data if d['wave_height'] is not None]
            swell_heights = [d['swell_wave_height'] for d in hourly_data if d['swell_wave_height'] is not None]
            swell_periods = [d['swell_wave_period'] for d in hourly_data if d['swell_wave_period'] is not None]
            
            # Count wave conditions
            wave_conditions = [d['wave_condition'] for d in hourly_data if d['wave_condition'] != 'Unknown']
            good_hours = wave_conditions.count('Good')
            ok_hours = wave_conditions.count('OK')
            bad_hours = wave_conditions.count('Bad')

            if wave_heights:
                daily_summary[date] = {
                    'max_wave_height': max(wave_heights),
                    'min_wave_height': min(wave_heights),
                    'avg_wave_height': sum(wave_heights) / len(wave_heights),
                    'max_swell_height': max(swell_heights) if swell_heights else None,
                    'avg_swell_period': sum(swell_periods) / len(swell_periods) if swell_periods else None,
                    'data_points': len(hourly_data),
                    'good_conditions_hours': good_hours,
                    'ok_conditions_hours': ok_hours,
                    'bad_conditions_hours': bad_hours,
                    'best_condition': 'Good' if good_hours > 0 else ('OK' if ok_hours > 0 else 'Bad')
                }

        return daily_summary

    def save_to_file(self, data: Dict[str, Any], filename: str = "marine_weather_data.json"):
        """
        Save data to a JSON file
        
        Args:
            data (Dict[str, Any]): Data to save
            filename (str): Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save data: {e}")

    def save_to_excel(self, data: Dict[str, Any], filename: str = "marine_weather_data.xlsx"):
        """
        Save data to an Excel file with multiple sheets
        
        Args:
            data (Dict[str, Any]): Data to save
            filename (str): Output Excel filename
        """
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Save raw data summary
                if 'raw_data' in data and 'hourly' in data['raw_data']:
                    raw_df = pd.DataFrame(data['raw_data']['hourly'])
                    raw_df.to_excel(writer, sheet_name='Raw_Hourly_Data', index=False)
                    logger.info("Raw hourly data saved to Excel")
                
                # Save processed data
                if 'processed_data' in data:
                    # Create a flattened DataFrame for processed data
                    processed_rows = []
                    for date, hourly_data in data['processed_data'].items():
                        for hour_data in hourly_data:
                            row = {
                                'date': date,
                                'hour': hour_data['hour'],
                                'timestamp': hour_data['timestamp'],
                                'wave_height': hour_data['wave_height'],
                                'wave_direction': hour_data['wave_direction'],
                                'wind_wave_height': hour_data['wind_wave_height'],
                                'wind_wave_direction': hour_data['wind_wave_direction'],
                                'swell_wave_height': hour_data['swell_wave_height'],
                                'swell_wave_direction': hour_data['swell_wave_direction'],
                                'swell_wave_period': hour_data['swell_wave_period'],
                                'wave_condition': hour_data['wave_condition']
                            }
                            processed_rows.append(row)
                    
                    if processed_rows:
                        processed_df = pd.DataFrame(processed_rows)
                        processed_df.to_excel(writer, sheet_name='Processed_Hourly_Data', index=False)
                        logger.info("Processed hourly data saved to Excel")
                
                # Save daily summary
                if 'daily_summary' in data:
                    daily_summary_rows = []
                    for date, summary in data['daily_summary'].items():
                        row = {
                            'date': date,
                            'max_wave_height': summary['max_wave_height'],
                            'min_wave_height': summary['min_wave_height'],
                            'avg_wave_height': summary['avg_wave_height'],
                            'max_swell_height': summary['max_swell_height'],
                            'avg_swell_period': summary['avg_swell_period'],
                            'data_points': summary['data_points'],
                            'good_conditions_hours': summary['good_conditions_hours'],
                            'ok_conditions_hours': summary['ok_conditions_hours'],
                            'bad_conditions_hours': summary['bad_conditions_hours'],
                            'best_condition': summary['best_condition']
                        }
                        daily_summary_rows.append(row)
                    
                    if daily_summary_rows:
                        daily_df = pd.DataFrame(daily_summary_rows)
                        daily_df.to_excel(writer, sheet_name='Daily_Summary', index=False)
                        logger.info("Daily summary saved to Excel")
                
                # Save metadata
                metadata = {
                    'Parameter': ['Latitude', 'Longitude', 'Data_Collection_Date', 'Forecast_Length_Days'],
                    'Value': [
                        data.get('metadata', {}).get('latitude', 'N/A'),
                        data.get('metadata', {}).get('longitude', 'N/A'),
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        data.get('metadata', {}).get('forecast_length', 'N/A')
                    ]
                }
                metadata_df = pd.DataFrame(metadata)
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
                logger.info("Metadata saved to Excel")
            
            logger.info(f"Data successfully saved to Excel file: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save Excel file: {e}")
            raise


def main():
    """Main function to demonstrate usage"""
    # Initialize the extractor
    extractor = MarineWeatherExtractor()
    


    # Fetch marine data
    raw_data = extractor.fetch_marine_data(length=7)

    if raw_data:
        # Process the data
        processed_data = extractor.process_wave_data(raw_data)

        if processed_data:
            # Generate daily summary
            daily_summary = extractor.get_daily_summary(processed_data)

            # Prepare data with metadata
            data_to_save = {
                'raw_data': raw_data,
                'processed_data': processed_data,
                'daily_summary': daily_summary,
                'metadata': {
                    'latitude': extractor.latitude,
                    'longitude': extractor.longitude,
                    'forecast_length': 7,
                    'collection_timestamp': datetime.now().isoformat()
                }
            }
            
            # Save results to both JSON and Excel
            extractor.save_to_file(data_to_save)
            extractor.save_to_excel(data_to_save)

            # Print summary
            print("\n=== Marine Weather Data Summary ===")
            print(f"Location: {extractor.latitude}, {extractor.longitude}")
            print(f"Data collected for {len(processed_data)} days")
            
            # Count total conditions across all days
            total_good = sum(summary['good_conditions_hours'] for summary in daily_summary.values())
            total_ok = sum(summary['ok_conditions_hours'] for summary in daily_summary.values())
            total_bad = sum(summary['bad_conditions_hours'] for summary in daily_summary.values())
            total_hours = total_good + total_ok + total_bad
            
            print(f"\n=== Overall Condition Distribution ===")
            print(f"Total Hours: {total_hours}")
            print(f"Good: {total_good} hours ({total_good/total_hours*100:.1f}%)")
            print(f"OK: {total_ok} hours ({total_ok/total_hours*100:.1f}%)")
            print(f"Bad: {total_bad} hours ({total_bad/total_hours*100:.1f}%)")

            for date, summary in daily_summary.items():
                print(f"\n{date}:")
                print(f"  Max Wave Height: {summary['max_wave_height']:.2f}m")
                print(f"  Avg Wave Height: {summary['avg_wave_height']:.2f}m")
                if summary['max_swell_height']:
                    print(f"  Max Swell Height: {summary['max_swell_height']:.2f}m")
                if summary['avg_swell_period']:
                    print(f"  Avg Swell Period: {summary['avg_swell_period']:.1f}s")
                print(f"  Wave Conditions: {summary['good_conditions_hours']} Good, {summary['ok_conditions_hours']} OK, {summary['bad_conditions_hours']} Bad")
                print(f"  Overall Rating: {summary['best_condition']}")
        else:
            print("Failed to process wave data")
    else:
        print("Failed to fetch marine data")


if __name__ == "__main__":
    main()

# Marine Weather Data Extractor

A Python script to fetch and process marine weather data from the Open-Meteo API for wave forecasting.

## Features

- Fetches marine weather data including wave height, direction, and swell information
- **7-day forecasts** for comprehensive weekly planning
- Processes hourly data into organized daily summaries
- Calculates daily statistics (max, min, average values)
- Saves data to JSON format
- Comprehensive error handling and logging
- Configurable coordinates and forecast length

## Installation

1. Ensure you have Python 3.7+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Dashboard

Launch the beautiful Streamlit dashboard:
```bash
streamlit run dashboard.py
```

The dashboard provides:
- **Real-time data fetching** from Open-Meteo API
- **Beach selection** for popular Tel Aviv area beaches with pre-configured coordinates
- **Interactive visualizations** including wave height trends, condition heatmaps, and direction charts
- **Beach comparison** feature to compare conditions across multiple beaches
- **Customizable parameters** (location, forecast period, date range)
- **Export functionality** (Excel, JSON, CSV)
- **Beautiful ocean-themed design** with responsive layout

### **🏖️ Available Beaches**

The dashboard includes pre-configured coordinates for popular Tel Aviv area beaches:

- **Gordon Beach** - Popular family beach with good facilities
- **Frishman Beach** - Central location with water sports
- **Bograshov Beach** - Relaxed atmosphere, good swimming
- **Jerusalem Beach** - Family-friendly with playground
- **Dolphinarium Beach** - Good swimming and sunbathing
- **Charles Clore Beach** - Popular surfing spot
- **Hilton Beach** - Surfing and water sports
- **Herzliya Beach** - Northern beach with marina
- **Bat Yam Beach** - Southern beach, family atmosphere
- **Holon Beach** - Southern location with good facilities

You can also use custom coordinates for any location.

## Testing

Run the test suite to verify wave condition assessment logic:
```bash
python test_wave_conditions.py
```

The test file includes comprehensive tests for:
- Wave condition thresholds
- Boundary conditions
- Edge cases for Israeli Mediterranean conditions

## Usage

### Basic Usage

Run the script directly to fetch 7 days of marine weather data:

```bash
python extract_info.py
```

### Programmatic Usage

```python
from extract_info import MarineWeatherExtractor

# Initialize with custom coordinates
extractor = MarineWeatherExtractor(latitude=32.08, longitude=34.77)

# Fetch data for 7 days
raw_data = extractor.fetch_marine_data(length=7)

# Process the data
processed_data = extractor.process_wave_data(raw_data)

# Get daily summary
daily_summary = extractor.get_daily_summary(processed_data)

# Save to file
extractor.save_to_file({
    'raw_data': raw_data,
    'processed_data': processed_data,
    'daily_summary': daily_summary
}, 'my_marine_data.json')

# Save to Excel
extractor.save_to_excel({
    'raw_data': raw_data,
    'processed_data': processed_data,
    'daily_summary': daily_summary
}, 'my_marine_data.xlsx')
```

## API Parameters

The script fetches the following marine weather parameters:
- `wave_height`: Total wave height
- `wave_direction`: Wave direction
- `wind_wave_height`: Wind-generated wave height
- `wind_wave_direction`: Wind-generated wave direction
- `swell_wave_height`: Swell wave height
- `swell_wave_direction`: Swell wave direction
- `swell_wave_period`: Swell wave period

## Excel Output Format

The Excel file contains multiple sheets for easy data analysis:

1. **Raw_Hourly_Data**: Complete hourly data from the API
2. **Processed_Hourly_Data**: Organized hourly data with date and hour columns, including wave condition ratings
3. **Daily_Summary**: Daily statistics including max/min/average values and wave condition counts
4. **Metadata**: Information about data collection location and timing

## Wave Condition Assessment

The script automatically assesses wave conditions for every hour based on Israeli Mediterranean coast characteristics:
- **Wave Height**: Optimal range 1.2-3.2m, acceptable 0.6-4.0m
- **Swell Height**: Minimum 0.5m for acceptable conditions
- **Swell Period**: Optimal 8-15s, minimum 5.5s for acceptable conditions

**Condition Ratings:**
- **Good**: Ideal surfing conditions with moderate waves and good swell
- **OK**: Acceptable conditions for various skill levels
- **Bad**: Unsuitable conditions (too small, too large, or poor swell quality)

*Note: Criteria are optimized for Mediterranean waves with conservative thresholds to ensure quality conditions.*

## Output

The script generates:
1. **Raw API data**: Complete response from the Open-Meteo API
2. **Processed data**: Hourly data organized by date
3. **Daily summary**: Statistics for each day including max/min/average values
4. **Console output**: Summary of the collected data
5. **JSON file**: All data saved to `marine_weather_data.json`
6. **Excel file**: All data saved to `marine_weather_data.xlsx` with multiple sheets

## Configuration

You can modify the default coordinates in the `MarineWeatherExtractor` class initialization:

```python
extractor = MarineWeatherExtractor(
    latitude=32.08,    # Default latitude
    longitude=34.77    # Default longitude
)
```

## Error Handling

The script includes comprehensive error handling for:
- Network request failures
- JSON parsing errors
- Invalid data structures
- File I/O operations

All errors are logged with timestamps for debugging.

## License

This project is open source and available under the MIT License.


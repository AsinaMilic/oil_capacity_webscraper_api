# Oil Capacity Scraper

A Flask web application that scrapes car model information and oil capacity based on license plate numbers.

## Features

- Scrape car model information (make, model, year, trim) using license plate numbers.
- Retrieve oil capacity information based on car model details.

## Prerequisites

- Python 3.7+
- ChromeDriver

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/oil_capacity_scraper.git
   cd oil_capacity_scraper

2. **Run the (web) app.py:**

   ```bash
   pip install -r requirements.txt
   python app.py

### Open the browser, go to local host and choose license plate. Plate exmample: FK207PD
3. **Open browser and navigate to **
   ```bash
   http://127.0.0.1:5000/get_oil_capacity?nr_plates=FK207PD

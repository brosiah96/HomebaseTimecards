HomebaseTimecards README

Overview:
HomebaseTimecards is a tool designed to streamline payroll processes for businesses that incorporate tips. It automatically integrates timecard information from Homebase with tip data from Square, calculating the distribution of tips based on the actual hours worked by each employee. This software is particularly useful for restaurants and other service industries where tip allocation based on worked hours is essential.

Installation Instructions:
1. Prerequisites:
   - Python 3.6 or higher is required.
   - Ensure you have valid API keys from Homebase and Square.

2. Clone the Repository:
   - Use the command: git clone https://github.com/brosiah96/HomebaseTimecards.git

3. Install Dependencies:
   - Navigate to the project directory: cd HomebaseTimecards
   - Install required Python packages: pip install -r requirements.txt

Configuration:
- Set up the necessary API keys in a file named config.py:
  HOME_BASE_API_KEY = 'your_homebase_api_key'
  LOCATION_UUID = 'your_location_uuid'
  SQUARE_ACCESS_TOKEN = 'your_square_access_token'

Usage:
- To run the application and generate the timecard and tip distribution report:
  python homebase_timecards.py
  The script will calculate the distribution of tips based on the hours logged in the timecards and output the results in a CSV file.

Contributing:
- Contributions to improve the functionality or address issues are welcome. Please refer to CONTRIBUTE.md for guidelines on contributing to this project.

License:
- This project is licensed under the MIT License. For more details, see LICENSE.md.

Support:
- For support, feature requests, or bug reports, please file an issue through the GitHub issue tracker.

This README aims to provide a clear understanding of the HomebaseTimecards project, ensuring users can effectively install, configure, and use the software.

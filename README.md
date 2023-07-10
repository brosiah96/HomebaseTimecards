# HomebaseTimecards
time card reports with Square credit tips included. 
Timecards and Tips Distribution Python Script
This script retrieves data about employees' timecards and received tips from a time management API (e.g., Homebase) and a payment processing API (e.g., Square). It then distributes the tips equally among the employees who were clocked in at the time the tip was made. Finally, it exports the results to a CSV file.

Pre-requisites
Make sure you have the following Python packages installed:

csv
datetime
pytz
requests
tabulate
The script requires the following authorization keys that must be provided in a config.py file:

TIME_MANAGEMENT_API_KEY - The API key to access the time management API.
LOCATION_UUID - The unique identifier for the location.
PAYMENT_API_ACCESS_TOKEN - The API key to access the payment processing API.
Classes and Functions
TimecardsRetriever - Class to fetch the timecards of the employees from the time management API.
EmployeeRetriever - Class to fetch employee details from the time management API.
PaymentsRetriever - Class to fetch payments including tips from the payment processing API.
TipDistributor - Class to distribute tips among the employees who were clocked in at the time the tip was made.
CSVWriter - Class to write the output to a CSV file.
main - The main function that coordinates the data retrieval, tips distribution, and writing the output.
Usage
Install all the necessary packages.
Ensure you have the config.py file with the necessary keys.
Run the script with the command python filename.py where filename is the name of your Python script.
The script will generate a CSV file with the timecard details of the employees and their respective tips received in the given time period.
Please note that the script retrieves data for a specified time period. If you wish to change this, please modify the start_date and end_date in the main function.

The output CSV file will include the following columns:

"First Name"
"Last Name"
"Credit Tips"
"Shift Start"
"Shift End"
"Shift Hours"
"Wage"
"Timecard ID"
"Earnings"
"Earnings with Tip"
The CSV file will be named in the format "Timecards YYYY-MM-DD to YYYY-MM-DD.csv", where the dates are the start and end dates of the data retrieval period. If you wish to change the name of the output file, you can do so in the CSVWriter class.

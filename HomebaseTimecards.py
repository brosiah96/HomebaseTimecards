import csv
import datetime
import pytz
import requests
from tabulate import tabulate
from config import HOME_BASE_API_KEY, LOCATION_UUID, SQUARE_ACCESS_TOKEN


class TimecardsRetriever:
    API_URL = "https://api.joinhomebase.com/locations/{location_uuid}/timecards"

    def __init__(self, api_key, location_uuid):
        self.api_url = self.API_URL.format(location_uuid=location_uuid)
        self.headers = {'Authorization': 'Bearer ' + api_key}
        self.employee_retriever = EmployeeRetriever(api_key, location_uuid)

    def fetch(self, start_date, end_date):
        response = requests.get(self.api_url, headers=self.headers, params={
            'start_date': start_date,
            'end_date': end_date,
        })
        if response.status_code != 200:
            print(f"Error retrieving timecards: {response.json()}")
            exit()

        timecards = response.json()

        extended_timecards = []
        for timecard in timecards:
            employee = self.employee_retriever.fetch(timecard['user_id'])
            wage = employee['job']['wage_rate']

            extended_timecards.append({
                **timecard,
                'clock_in': self._convert_to_arizona_time(timecard['clock_in']),
                'clock_out': self._convert_to_arizona_time(timecard['clock_out']),
                'wage': wage,
            })

        return extended_timecards

    @staticmethod
    def _convert_to_arizona_time(time_string):
        time_object = datetime.datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S%z")
        return time_object.astimezone(pytz.timezone('America/Phoenix')).isoformat()


class EmployeeRetriever:
    EMPLOYEE_API_URL = "https://api.joinhomebase.com/locations/{location_uuid}/employees/{id}"

    def __init__(self, api_key, location_uuid):
        self.employee_api_url = self.EMPLOYEE_API_URL
        self.headers = {'Authorization': 'Bearer ' + api_key}
        self.location_uuid = location_uuid

    def fetch(self, employee_id):
        response = requests.get(
            self.employee_api_url.format(location_uuid=self.location_uuid, id=employee_id),
            headers=self.headers
        )
        if response.status_code != 200:
            print(f"Error retrieving employee data: {response.json()}")
            exit()

        employee = response.json()
        return employee


class PaymentsRetriever:
    API_URL = "https://connect.squareup.com/v2/payments"

    def __init__(self, access_token):
        self.headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }

    def fetch(self, start_date, end_date):
        payments = []
        cursor = None
        while True:
            response = requests.get(self.API_URL, headers=self.headers,
                                    params=self._get_params(start_date, end_date, cursor))
            if response.status_code != 200:
                print(f"Error retrieving Square payments: {response.json()}")
                exit()
            data = response.json()
            payments += data.get('payments', [])
            cursor = data.get('cursor', None)
            if not cursor:
                break

        for payment in payments:
            payment['created_at'] = self._convert_to_arizona_time(payment['created_at'])

        return payments

    @staticmethod
    def _get_params(start_date, end_date, cursor):
        params = {
            'begin_time': start_date + 'T00:00:00Z',
            'end_time': end_date + 'T23:59:59Z',
        }
        if cursor:
            params['cursor'] = cursor

        return params

    @staticmethod
    def _convert_to_arizona_time(time_string):
        time_object = datetime.datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.UTC)
        return time_object.astimezone(pytz.timezone('America/Phoenix')).isoformat()


class TipDistributor:
    def distribute(self, square_tips, timecards):
        tips_per_shift = {}

        for timecard in timecards:
            shift_key = (timecard['first_name'], timecard['last_name'], timecard['clock_in'],
                         timecard['clock_out'], timecard['wage'], timecard['id'])
            tips_per_shift.setdefault(shift_key, 0)

        for tip in square_tips:
            tip_amount_dollars = round(tip['amount_money']['amount'] / 100, 2)
            tip_time = datetime.datetime.fromisoformat(tip['created_at'])
            workers_at_tip_time = [
                timecard for timecard in timecards
                if datetime.datetime.fromisoformat(timecard['clock_in']) <= tip_time
                   <= datetime.datetime.fromisoformat(timecard['clock_out'])
            ]

            if not workers_at_tip_time:
                print(
                    f"No workers clocked in at the time of tip {tip['id']} at {tip['created_at']} amount $"
                    f"{tip_amount_dollars}")
                continue

            tip_per_worker = round(tip_amount_dollars / len(workers_at_tip_time), 2)

            for worker in workers_at_tip_time:
                shift_key = (
                    worker['first_name'], worker['last_name'], worker['clock_in'], worker['clock_out'], worker['wage'],
                    worker['id'])
                tips_per_shift.setdefault(shift_key, 0)
                tips_per_shift[shift_key] += tip_per_worker
                tips_per_shift[shift_key] = round(tips_per_shift[shift_key], 2)

        return self._prepare_output(tips_per_shift)

    def _prepare_output(self, tips_per_shift):
        sorted_tips = sorted(tips_per_shift.items(), key=lambda shift: (shift[0][0], shift[0][1], shift[0][2]))

        result_data = []
        prev_employee = None
        total_tips, total_hours, total_earnings, total_earnings_with_tip = 0, 0, 0, 0
        for shift in sorted_tips:
            employee = (shift[0][0], shift[0][1])
            if prev_employee and prev_employee != employee:
                result_data.append((*prev_employee, f"${round(total_tips, 2)}", '', '', round(total_hours, 2), '', '',
                                    f"${round(total_earnings, 2)}", f"${round(total_earnings_with_tip, 2)}"))
                result_data.append(('', '', '', '', '', '', '', '', '', '', '', ''))
                total_tips, total_hours, total_earnings, total_earnings_with_tip = 0, 0, 0, 0
            start_time = datetime.datetime.strptime(shift[0][2], "%Y-%m-%dT%H:%M:%S%z").strftime('%m-%d-%Y %H:%M:%S')
            end_time = datetime.datetime.strptime(shift[0][3], "%Y-%m-%dT%H:%M:%S%z").strftime('%m-%d-%Y %H:%M:%S')
            shift_hours = round((datetime.datetime.strptime(shift[0][3], "%Y-%m-%dT%H:%M:%S%z") -
                                 datetime.datetime.strptime(shift[0][2], "%Y-%m-%dT%H:%M:%S%z")).seconds / 3600, 2)
            earnings = round(shift_hours * shift[0][4], 2)
            earnings_with_tip = round(earnings + shift[1], 2)

            total_tips += shift[1]
            total_hours += shift_hours
            total_earnings += earnings
            total_earnings_with_tip += earnings_with_tip

            result_data.append((*employee, f"${round(shift[1], 2):.2f}", start_time, end_time, shift_hours,
                                f"${shift[0][4]:.2f}", shift[0][5], f"${earnings}", f"${earnings_with_tip}"))

            prev_employee = employee

        result_data.append((*prev_employee, f"${round(total_tips, 2)}", '', '', round(total_hours, 2), '', '',
                            f"${round(total_earnings, 2)}", f"${round(total_earnings_with_tip, 2)}"))

        return result_data


class CSVWriter:
    def write(self, data, start_date, end_date, filename=None):
        if filename is None:
            filename = f"YOUR COMPANY Timecards {start_date} to {end_date}.csv"

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ["First Name", "Last Name", "Credit Tips", "Shift Start", "Shift End", "Shift Hours", "Wage",
                 "Timecard ID", "Earnings", "Earnings with Tip"])
            for row in data:
                writer.writerow(row)


def main():
    timecards_service = TimecardsRetriever(HOME_BASE_API_KEY, LOCATION_UUID)
    payments_service = PaymentsRetriever(SQUARE_ACCESS_TOKEN)
    tip_distributor = TipDistributor()

    start_date = "2023-06-25"
    end_date = "2023-07-08"

    timecards = timecards_service.fetch(start_date, end_date)
    payments = payments_service.fetch(start_date, end_date)

    square_tips = [
        {'id': payment['id'], 'created_at': payment['created_at'],
         'amount_money': payment.get('tip_money', {'amount': 0})}
        for payment in payments if payment.get('tip_money', {'amount': 0})['amount'] > 0]
    tips_per_shift = tip_distributor.distribute(square_tips, timecards)

    print(f"Received {len(timecards)} timecards")
    print(f"Received {len(payments)} payments")
    print(f"Received {len(square_tips)} credit tips")
    print("From:", start_date, "TO:", end_date)
    print(tabulate(tips_per_shift,
                   headers=["First Name", "Last Name", "Credit Tips", "Shift Start", "Shift End", "Shift Hours", "Wage",
                            "Timecard ID", "Earnings", "Earnings with Tip"]))
    csv_writer = CSVWriter()
    csv_writer.write(data=tips_per_shift, start_date=start_date, end_date=end_date)


if __name__ == "__main__":
    main()

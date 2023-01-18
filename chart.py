import requests
from randomcolor import RandomColor
import matplotlib.pyplot as plt
from decimal import Decimal
import dateutil
from datetime import datetime
import re
import argparse
import csv

parser = argparse.ArgumentParser()
parser.add_argument("--start-date", help="Start date in format yyyy-mm-dd")
parser.add_argument("--end-date", help="End date in format yyyy-mm-dd")
parser.add_argument("--output", help="If set to 'pdf' or 'png', it will output a file  in these formats")
parser.add_argument("--debug", help="If set to true, dumps djbcd data to log output")
args = parser.parse_args()

try:
  date_format = "%Y-%m-%d"
  datetime.strptime(args.start_date, date_format)
  datetime.strptime(args.end_date, date_format)
  start_date = args.start_date
  end_date = args.end_date
except:
  print("Invalid date format supplied, please use --start-date yyyy-mm-dd and --end-date yyyy-mm-dd")
  exit()

# Function to replace dates in URL with given dates in parameters
def replace_dates(string):
  date_pattern = r"(\d{4})-(\d{2})-(\d{2})"
  matches = re.finditer(date_pattern, string)

  match_list = [match.group() for match in matches]
  string = re.sub(r"\b"+match_list[0]+r"\b", start_date, string, count=1)
  string = re.sub(r"\b"+match_list[1]+r"\b", end_date, string, count=1)

  return string

# Function to convert djbcd format into dictionary and convert the values to decimals
def convert_djbcd(url):
  source_data = requests.get(url).content.decode("utf-8")

  # Split dates and values on space character, then on comma
  dates = [dateutil.parser.parse(i) for i in list(source_data.split(" ")[0].split(","))]
  values = list(source_data.split(" ")[1].split(","))
  values = [Decimal(float(value)) for value in values]

  if args.debug:
    for k, v in dict(zip(dates, values)).items():
      print(f"The date is {k} with value {v}\n")

  output = {}

  output["dates"] = dates
  output["values"] = values

  return output

# Function to render a chart for each URL given
def create_chart(data):
  fig, axs = plt.subplots(len(data))
  if len(data) > 1:
    fig.suptitle(f'Comparison of {len(data)} data sets')
  else:
    fig.suptitle(f'Data set')

  fig.set_figwidth(12)
  fig.set_figheight(4)
  fig.canvas.manager.set_window_title('Graphs from MoneyDJ data')

  # Create chart using matplotlib
  for index, (name, url) in enumerate(data.items()):
    url = replace_dates(url)
    dates = convert_djbcd(url)['dates']
    values = convert_djbcd(url)['values']

    # Render charts
    rc = RandomColor()
    color = rc.generate(luminosity='dark', format_='hex')[0]
    axs[index].plot(dates, values, color)
    axs[index].set_title(label=name, color=color)
    axs[index].set
  plt.tight_layout()

  # Save chart to desired output
  if args.output == "pdf" or args.output == "png":
    plt.savefig(f'chart-{datetime.now().strftime("%Y%m%d%H%M%S")}.{args.output}', bbox_inches='tight')

  # Render the chart in the GUI
  plt.show()

# Read names and URLs from CSV file
with open('moneydj.csv', 'r') as file:
  reader = csv.reader(file)
  data = {}

  for row in reader:
    name = row[0]
    url = row[1]
    data[name] = url

create_chart(data)
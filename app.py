from flask import Flask, render_template, request
from xml.dom import minidom

doc = minidom.parse("transport.xml")

app = Flask(__name__)

import xml.etree.ElementTree as Et

tree = Et.parse('transport.xml')
root = tree.getroot()

# Map station IDs to names
stations = {}
for station in root.findall('.//station'):
    stations[station.get('id')] = station.get('name')


@app.route('/')
def home():
    lines = load_all_data()
    wilayas = set()
    trains = set()

    for line in root.findall('.//line'):
        wilayas.add(stations.get(line.get('departure'), line.get('departure')))
        wilayas.add(stations.get(line.get('arrival'), line.get('arrival')))

        for trip in line.find('trips').findall('trip'):
            trains.add(trip.get('type'))

    wilayas = sorted(list(wilayas))
    trains = sorted(list(trains))

    print("Wilayas:", wilayas)
    print("Trains:", trains)
    return render_template("index.html", wilayas=wilayas, trains=trains, lines=lines)


@app.route('/filter')
def filter():
    departure = request.args.get('departure')
    arrival = request.args.get('arrival')
    train_type = request.args.get('type')
    max_price = request.args.get('max_price')
    lines = []
    wilayas = set()
    trains = set()

    for line in root.findall('.//line'):
        wilayas.add(stations.get(line.get('departure'), line.get('departure')))
        wilayas.add(stations.get(line.get('arrival'), line.get('arrival')))

        for trip in line.find('trips').findall('trip'):
            trains.add(trip.get('type'))

    wilayas = sorted(list(wilayas))
    trains = sorted(list(trains))

    for line in root.findall('.//line'):
        dep = stations.get(line.get('departure'), line.get('departure'))
        arr = stations.get(line.get('arrival'), line.get('arrival'))

        if departure and dep != departure:
            continue
        if arrival and arr != arrival:
            continue

        for trip in line.find('trips').findall('trip'):
            if train_type and trip.get('type') != train_type:
                continue
            classes = trip.findall('class')
            valid_price = False
            if max_price:
                for c in classes:
                    if float(c.get('price')) <= float(max_price):
                        valid_price = True
                        break
                if not valid_price:
                    continue

            schedule = trip.find('schedule')
            lines.append({
                "code": line.get("code"),
                "departure": dep,
                "arrival": arr,
                "trips": [{
                    "code": trip.get('code'),
                    "type": trip.get('type'),
                    "departure_time": schedule.get('departure'),
                    "arrival_time": schedule.get('arrival'),
                    "classes": [
                        {"type": c.get('type'),
                         "price": c.get('price')}
                        for c in classes
                    ]
                }]
            })
    return render_template('index.html', lines=lines, wilayas=wilayas, trains=trains)


def count_trips_per_type():
    counts = {}
    for trip in root.findall('.//trip'):
        t = trip.get('type')
        if t not in counts:
            counts[t] = 0
        counts[t] += 1


def price_stats():
    stats = {}
    for line in root.findall('.//line'):
        line_code = line.get('code')
        prices = []
        for trip in line.find('trips').findall('trip'):
            for c in trip.findall('class'):
                prices.append(float(c.get('price')))

        if prices:
            stats[line_code] = {
                "min": min(prices),
                "max": max(prices)
            }

    return stats


@app.route('/search')
def search():
    code = request.args.get('code')
    trips = doc.getElementsByTagName("trip")
    for trip in trips:
        if trip.getAttribute("code") == code:
            schedule = trip.getElementsByTagName("schedule")[0]
            classes = trip.getElementsByTagName("class")
            line_elem = trip.parentNode.parentNode
            dep_id = line_elem.getAttribute("departure")
            arr_id = line_elem.getAttribute("arrival")
            dep_name = stations.get(dep_id, dep_id)
            arr_name = stations.get(arr_id, arr_id)
            print("schedule:", schedule.getAttribute("departure"))
            return render_template('index.html', lines=[{
                "code": line_elem.getAttribute("code"),
                "departure": dep_name,
                "arrival": arr_name,
                "trips": [{
                    "code": code,
                    "departure_time": schedule.getAttribute("departure"),
                    "arrival_time": schedule.getAttribute("arrival"),
                    "type": trip.getAttribute("type"),
                    "classes": [
                        {
                            "type": c.getAttribute("type"),
                            "price": c.getAttribute("price")
                        }
                        for c in classes
                    ],
                    "days": trip.getAttribute("days")
                }]
            }])
    return render_template('index.html', lines=[])


def load_all_data():
    lines = []

    for line in root.findall('.//line'):
        dep = stations.get(line.get('departure'), line.get('departure'))
        arr = stations.get(line.get('arrival'), line.get('arrival'))

        line_data = {
            "code": line.get('code'),
            "departure": dep,
            "arrival": arr,
            "trips": []
        }

        for trip in line.find('trips').findall('trip'):
            schedule = trip.find('schedule')

            trip_data = {
                "code": trip.get('code'),
                "type": trip.get('type'),
                "departure_time": schedule.get('departure'),
                "arrival_time": schedule.get('arrival'),
                "classes": []
            }

            for c in trip.findall('class'):
                trip_data["classes"].append({
                    "type": c.get('type'),
                    "price": c.get('price')
                })

            line_data["trips"].append(trip_data)

        lines.append(line_data)

    return lines


if __name__ == '__main__':
    app.run(debug=True)
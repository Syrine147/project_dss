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

    return render_template("index.html", wilayas=wilayas, trains=trains, lines=lines, stats=None)


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

    return render_template('index.html', lines=lines, wilayas=wilayas, trains=trains, stats=None)


def get_statistics():
    """
    Uses ElementTree to compute:
    - Cheapest and most expensive trip (by min price) per line
    - Number of trips per train type
    """
    # --- Price stats per line (cheapest & most expensive) ---
    price_stats = {}
    for line in root.findall('.//line'):
        line_code = line.get('code')
        dep = stations.get(line.get('departure'), line.get('departure'))
        arr = stations.get(line.get('arrival'), line.get('arrival'))

        trip_min_prices = []  # (min_price, trip_code) for each trip
        for trip in line.find('trips').findall('trip'):
            prices = [float(c.get('price')) for c in trip.findall('class')]
            if prices:
                trip_min_prices.append((min(prices), trip.get('code')))

        if trip_min_prices:
            cheapest = min(trip_min_prices, key=lambda x: x[0])
            most_expensive = max(trip_min_prices, key=lambda x: x[0])
            price_stats[line_code] = {
                "route": f"{dep} → {arr}",
                "cheapest_price": cheapest[0],
                "cheapest_trip": cheapest[1],
                "expensive_price": most_expensive[0],
                "expensive_trip": most_expensive[1],
            }

    # --- Trips count per train type ---
    type_counts = {}
    for trip in root.findall('.//trip'):
        t = trip.get('type')
        type_counts[t] = type_counts.get(t, 0) + 1

    return {
        "price_stats": price_stats,
        "type_counts": type_counts
    }


@app.route('/stats')
def stats_page():
    wilayas = set()
    trains = set()
    for line in root.findall('.//line'):
        wilayas.add(stations.get(line.get('departure'), line.get('departure')))
        wilayas.add(stations.get(line.get('arrival'), line.get('arrival')))
        for trip in line.find('trips').findall('trip'):
            trains.add(trip.get('type'))
    wilayas = sorted(list(wilayas))
    trains = sorted(list(trains))
    stats = get_statistics()
    return render_template('index.html', lines=[], wilayas=wilayas, trains=trains, stats=stats, show_stats=True)


@app.route('/search')
def search():
    code = request.args.get('code')
    trips = doc.getElementsByTagName("trip")
    wilayas = set()
    trains = set()
    for line in root.findall('.//line'):
        wilayas.add(stations.get(line.get('departure'), line.get('departure')))
        wilayas.add(stations.get(line.get('arrival'), line.get('arrival')))
        for trip in line.find('trips').findall('trip'):
            trains.add(trip.get('type'))
    wilayas = sorted(list(wilayas))
    trains = sorted(list(trains))

    for trip in trips:
        if trip.getAttribute("code") == code:
            schedule = trip.getElementsByTagName("schedule")[0]
            classes = trip.getElementsByTagName("class")
            line_elem = trip.parentNode.parentNode
            dep_id = line_elem.getAttribute("departure")
            arr_id = line_elem.getAttribute("arrival")
            dep_name = stations.get(dep_id, dep_id)
            arr_name = stations.get(arr_id, arr_id)
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
            }], wilayas=wilayas, trains=trains, stats=None)
    return render_template('index.html', lines=[], wilayas=wilayas, trains=trains, stats=None)


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
import csv
from skyfield.api import load, Topos
from skyfield import almanac
from datetime import datetime


def planetMeridianTransit(planet, start, end, latitude=0, longitude=0):
    observer = Topos(latitude_degrees=latitude, longitude_degrees=longitude)

    ts = load.timescale()
    y1, m1, d1 = start.split('/')
    y2, m2, d2 = end.split('/')

    # Convert to proper date-time format
    t0 = ts.utc(2000 + int(y1), int(m1), int(d1))
    t1 = ts.utc(2000 + int(y2), int(m2), int(d2))

    planets = load('de421.bsp')
    target = planets[planet]
    f = almanac.meridian_transits(planets, target, observer)

    # Finding discrete meridian transits
    transits = almanac.find_discrete(t0, t1, f)

    transit_time = transits[0]  # Picking the first transit time
    dt = transit_time.utc_strftime('%Y/%m/%d %H:%M:%S')
    dt = dt[1::2]
    dts = []
    for dt1 in dt:
        dts.append(dt1.split(' '))
    return dts


def planetLocation(planet, date, time, latitude=0, longitude=0):
    planets = load('de421.bsp')
    earth = planets['earth']
    target = planets[planet]

    # Convert date and time to Skyfield time
    ts = load.timescale()
    dt = datetime.strptime(f"{date} {time}", "%Y/%m/%d %H:%M:%S")
    sky_time = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

    # Define observer's location
    observer = earth + Topos(latitude_degrees=latitude,
                             longitude_degrees=longitude)

    # Get the apparent position of the planet
    astrometric = observer.at(sky_time).observe(target).apparent()

    # Get the altitude and azimuth
    alt, az, _ = astrometric.altaz()

    return az.degrees, alt.degrees, dt


def save_data_to_csv(data, filename='data/marsData.csv'):
    # Write data to a CSV file
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Date", "Time", "Azimuth (degrees)",
             "Altitude (degrees)"])  # Header row
        for row in data:
            writer.writerow(row)


start = "25/01/01"
end = "25/12/31"
planets = ["mercury", "venus", "mars"]
for planet_name in planets:
    # Find meridian transit time
    dts = planetMeridianTransit(planet_name, start, end)

    # Data list to store rows
    data_rows = []

    for dt in dts:
        date = dt[0]
        #time = dt[1]
        time = "12:00:00"
        az, alt, dt = planetLocation(planet_name, date, time)

        # Collect data for each transit
        data_rows.append([date, time, az, alt])

    # Save the collected data to CSV file
    save_data_to_csv(data_rows, f'data/{planet_name}Data.csv')

    print(f"Data saved to data/{planet_name}Data.csv")

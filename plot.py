import csv
import matplotlib.pyplot as plt

# Read data from the CSV file
azimuths = []
altitudes = []
days = []  # The day is determined by row index

planets = ["Mercury", "Venus", "Mars"]
planet_num = 0
planet = planets[planet_num]


# run through calculated data csv for target planet, and write azimuth and altitude data to respective arrays
with open(f'data/{planet.lower()}Data.csv', mode='r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header
    
    for i, row in enumerate(reader):
        day = i  # Day is determined by row index (starting from 0)
        azimuth = float(row[2])
        altitude = float(row[3])
        
        
        days.append(day)
        azimuths.append(azimuth)
        altitudes.append(altitude)

# extend to -720, 720
azimuths += [(azimuth - 360) for azimuth in azimuths]
altitudes += altitudes

# Plot Azimuth vs. Altitude
plt.figure(figsize=(12, 6))

# plot azimuth, altitude on x-y
plt.scatter(azimuths, altitudes, color='g', marker='o', label=f"{planet} Position")

# Set axis limit to show one 'period' of the analemma
plt.xlim([-110, -190, -55][planet_num], [250, 120, 185][planet_num])

# Labels and title
plt.xlabel("Azimuth (degrees)")
plt.ylabel("Altitude (degrees)")
plt.title(f"{planet} Analemma")
plt.grid(True)
plt.legend()


plt.show()
print('Done')

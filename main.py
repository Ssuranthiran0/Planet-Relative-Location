from math import sin, cos, tan, atan, sqrt, pi, degrees
import sympy as sp
from datetime import datetime



ECCENTRICITY = 0
SEMIMAJOR = 1
ORBITALPERIOD = 2
INCLINATION = 3
MEANANOMALY = 4
LONGITUDEPERIHELION = 5

mercury= (0.206, 0.387, 88, 0.122, 3.049, 1.351, "Mercury")
venus= (0.007, 0.723, 224.701, 0.0592, 0.874, 2.295, "Venus")
earth= (0.017, 1, 365.256, 0, 6.24, 1.795, "Earth")
mars= (0.093, 1.524, 686.98, 0.0323, 0.338, 5.86, "Mars")

planets = [mercury, venus, earth, mars]

### Orbital equations

## Orbits 

# calculate the orbital path of a planet given a mean anomaly and its 
def calculatePolarOrbit(anomaly, planet):
    return planet[SEMIMAJOR] * (1 - planet[ECCENTRICITY] ** 2) / (1 + planet[ECCENTRICITY] * cos(anomaly + planet[LONGITUDEPERIHELION]))

def polarToCartesian(polar):
    r = polar[0]
    theta = polar[1]
    return (r*cos(theta), r*sin(theta))

## calculate anomalies given 

def calculateAngle(anomaly, eccentricity):
    return calculateTrueAnomaly(calculateEccentricAnomaly(anomaly, eccentricity), eccentricity)

# convert true anomaly if given eccentric
def calculateTrueAnomaly(anomaly, eccentricity):
    return 2 * atan( sqrt((1 + eccentricity) / (1 - eccentricity)) * tan(anomaly/2))

# calculate eccentric anomaly if given mean using kepters equation and newton's method
def calculateEccentricAnomaly(anomaly, eccentricity, tolerance=1e-6):

    E = sp.symbols('E')
    
    # Define Kepler's equation: mean = eccentric - eccentricity * sin(E)
    f = E - eccentricity * sp.sin(E) - anomaly
    
    # Calculate the derivative of f
    f_diff = sp.diff(f, E)
    
    # Guess that the eccentric anomaly is the same as the given mean anomaly to begin with
    e = anomaly
    
    # keep repeating the process. stop if it is over 100 iterations
    for i in range(100):
        # Calculate f(e) and f'(e) for the current e values
        f_e = f.subs(E, e)
        f_diff_e = f_diff.subs(E, e)
        
        # subtract the error from the guess to narrow it down
        e1 = e - f_e / f_diff_e
        
        # check to see if the difference is low enough
        if abs(e1 - e) < tolerance:
            return e1
        
        # Update the value of E
        e = e1
    return e

# calculate mean anomaly based on time since epoch and planet
def determineCurrentMean(time, planet):
    return (planet[MEANANOMALY] + 2 * pi / planet[ORBITALPERIOD] * timeSinceEpoch(time)) % (2*pi)

def determineCurrentPolar(time, planet):
    current_true = calculateAngle(determineCurrentMean(time, planet), planet[ECCENTRICITY])
    return (calculatePolarOrbit(current_true, planet), current_true)

def determineCurrentCartesian(time, planet):
    return polarToCartesian(determineCurrentPolar(time, planet))

# time since epoch, in 2025/27/02 form

def timeSinceEpoch(date):
    # convert to julian time, when the epoch j2000 is
    def julian(year, month, day):
        if month <= 2:
            month += 12
            year -= 1
        # century
        A = year // 100
        # correction (julian -> gregorian)
        B = 2 - A + (A // 4)

        # equation to calculate julian time
        return int(365.25 * (year+4716)) + int(30.6001 * (month + 1)) + day + B - 1534
    
    #defined
    j2000 = 2451535

    date_num = datetime.strptime(date, "%Y/%m/%d") # split the given time string into the actual time

    # find today's julian date
    current_date = julian(date_num.year, date_num.month, date_num.day)

    time_elapsed = current_date - j2000
    
    return round(time_elapsed)

day1 = "2025/02/27"

t = []
t_deg = []
names = []
for planet in planets:
    mean = determineCurrentMean(day1, planet)
    t.append("{:.3e}".format(mean))
    t_deg.append("{:.3e}".format(degrees(mean)))
    names.append(planet[-1])

for i in range(len(t)):
    print(names[i] + ":     Mean Anomaly Radians: " + t[i] + "    Degrees: " + t_deg[i])

'''
DATA
2025/02/27 'day 1'
MEAN ANOMALIES
DATA: JPL HORIZONS SYSTEM time 2025-02-26 to 2025-02-27
Mercury: 3.33e2 PREDICTED 3.26e2 ERROR 2.10%
Venus:   1.15e1 PREDICTED 1.20e1 ERROR 4.35%
Earth:   5.16e1 PREDICTED 5.43e1 ERROR 5.23%
Mars:    1.54e2 PREDICTED 1.55e2 ERROR 0.65%
'''
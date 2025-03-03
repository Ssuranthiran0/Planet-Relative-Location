from math import sin, cos, pi, radians, degrees, acos, fabs
import sympy as sp
from datetime import datetime

ECCENTRICITY = 0
SEMIMAJOR = 1
ORBITALPERIOD = 2
INCLINATION = 3
MEANANOMALY = 4
LONGITUDEPERIHELION = 5

mercury = (0.205630, 0.387098, 87.9691, 0.12226031, 3.050765719, 1.35184477,
           "Mercury")
venus = (0.007, 0.723, 224.701, 0.0592, 0.874, 2.295, "Venus")
earth = (0.017, 1, 365.256, 0, 6.24, 1.795, "Earth")
mars = (0.093, 1.524, 686.98, 0.0323, 0.338, 5.86, "Mars")

planets = [mercury, venus, earth, mars]

### Orbital equations

## Orbits


# calculate the orbital path of a planet given a mean anomaly and its name
def calculatePolarOrbit(anomaly, planet):
    return planet[SEMIMAJOR] * (1 - planet[ECCENTRICITY]**2) / (
        1 + planet[ECCENTRICITY] * cos(anomaly + planet[LONGITUDEPERIHELION]))


def polarToCartesian(polar):
    r = polar[0]
    theta = polar[1]
    return (r * cos(theta), r * sin(theta))


## calculate anomalies given


# essentially a wrapper for the calculations (give it mean, it gives true)
def calculateAngle(anomaly, eccentricity):
    eccentric = calculateEccentricAnomaly(anomaly, eccentricity)
    angle = calculateTrueAnomaly(eccentric, eccentricity)
    return angle if eccentric < pi else 2 * pi - angle


# convert true anomaly if given eccentric
def calculateTrueAnomaly(anomaly, eccentricity):
    return acos(
        (cos(anomaly) - eccentricity) / (1 - eccentricity * cos(anomaly)))


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
    return (planet[MEANANOMALY] +
            2 * pi / planet[ORBITALPERIOD] * timeSinceEpoch(time)) % (2 * pi)


# determine the current polar position of a planet given current time and planet
def determineCurrentPolar(time, planet):
    current_true = calculateAngle(determineCurrentMean(time, planet),
                                  planet[ECCENTRICITY])
    return (calculatePolarOrbit(current_true, planet), current_true)


# determine the current cartesian position of a planet given current time and planet
def determineCurrentCartesian(time, planet):
    return polarToCartesian(determineCurrentPolar(time, planet))


# time since epoch, in YYYY/MM/DD form
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
        return int(365.25 * (year + 4716)) + int(30.6001 *
                                                 (month + 1)) + day + B - 1534

    #defined
    j2000 = 2451535

    date_num = datetime.strptime(
        date, "%Y/%m/%d")  # split the given time string into the actual time

    # find today's julian date
    current_date = julian(date_num.year, date_num.month, date_num.day)

    time_elapsed = current_date - j2000

    return round(time_elapsed)


# actual values from 2/25 -> 2/28 from JPL HORIZONS SYSTEM
days = ["2025/02/25", "2025/02/26", "2025/02/27", "2025/02/28"]
actualMAdeg = [
    329.0228881459024, 333.1152332316329, 337.2075795856536, 341.2999268344714
]
actualMA = [
    5.742532712567018, 5.813957608440824, 5.885382526450472, 5.956807460077274
]
actualTruedeg = [
    313.7050431465037, 319.4725025057658, 325.3771710165047, 331.4058479446206
]
actualTrue = [
    5.475185883017362, 5.575847038311449, 5.678902945062672, 5.784123206997312
]


# test function
def testValues(days, planet, actualMA, actualTA, decimals=3):
    means = []
    trues = []
    errs = []
    eccentricity = planet[ECCENTRICITY]
    print("\n\033[1;36;40m-------------------------\033[1;37;40m")
    for i in range(len(days)):
        m1 = determineCurrentMean(days[i], planet)
        t1 = calculateAngle(m1, eccentricity)
        means.append(m1)
        trues.append(t1)
        print(f"\033[1;31;40m{days[i]} \033[1;37;40m")

        # add to errors array
        errs.append(round(fabs(m1 - actualMA[i]) / actualMA[i] * 100, 2))
        errs.append(round(fabs(t1 - actualTrue[i]) / actualTrue[i] * 100, 2))

        # print in this order: predicted, actual, and error for mean anomalies
        print(f"\nPredicted Mean Anomaly: {round(degrees(m1), decimals)}")
        print(f"Actual Mean Anomaly: {round(actualMAdeg[i], decimals)}")
        print(f"Mean Anomaly Error: {errs[-2]}%\n")

        # do the same for true anomaly
        print(f"Predicted True Anomaly: {round(degrees(t1), decimals)}")
        print(f"Actual True Anomaly: {round(actualTruedeg[i], decimals)}")
        print(f"True Anomaly Error: {errs[-1]}%")

        polar = calculatePolarOrbit(t1, planet)
        cartesian = polarToCartesian((polar, t1))
        print(
            f"\n\nApproximate Polar Position: {round(polar, decimals)} AU at {round(degrees(t1), decimals)} degrees"
        )
        print(
            f"Approximate Cartesian Position: ({round(cartesian[0], decimals)}, {round(cartesian[1], decimals)}) AU"
        )
        # simple seperators for ease of viewing
        print("\n\033[1;36;40m-------------------------\033[1;37;40m")
    print("\033[1;36;40m-------------------------")
    print("\033[1;36;40m-------------------------\033[1;37;40m")
    # take sum of odd errors for mean anomaly values
    print("Average Mean Anomaly Error: " +
          str(round(sum(errs[0:len(days)]) / len(days), 2)) + "%")
    # take sum of even errors for true anomaly values
    print("Average True Anomaly Error: " +
          str(round(sum(errs[len(days):len(days) * 2]) / len(days), 2)) + "%")


testValues(days, mercury, actualMA, actualTrue, 5)
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

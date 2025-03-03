from flask import Flask, render_template, request
import main  # Import your main.py script that contains the calculations

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        mean = request.form.get('mean')
        date_input = request.form.get('date')  # Get user input for date
        planet_name = request.form.get('planet')  # Get selected planet
        print(f"Inputted Mean Anomaly: {mean}")
        if(type(mean) is str):
            mean = float(mean)
        else:
            mean = 0.0
        mean = main.radians(mean)
        true = main.calculateAngle(mean, 0.206)
        true = main.degrees(true)
        print(f"Calculated Anomaly: {true}")
        print(f"Date Input: {date_input}")
        print(f"Planet Name: {planet_name}")

        # Find the correct planet from the list
        planet = next((p for p in main.planets if p[-1] == planet_name), None)

        if planet:
            
            mean_anomaly = main.determineCurrentMean(date_input, planet)
            true_anomaly = main.calculateAngle(mean_anomaly,
                                               planet[main.ECCENTRICITY])

            print(
                f"Mean Anomaly      Radians: {mean_anomaly:.3e}    Degrees: {main.degrees(mean_anomaly):.3e}"
            )
            print(
                f"True Anomaly      Radians: {true_anomaly:.3e}    Degrees: {main.degrees(true_anomaly):.3e}"
            )

            # Properly formatted HTML output
            result = f"""
                <strong>Mean Anomaly</strong><br>
                Radians: {mean_anomaly:.3e}    Degrees: {main.degrees(mean_anomaly):.3e}<br><br>
                <strong>True Anomaly</strong><br>
                Radians: {true_anomaly:.3e}    Degrees: {main.degrees(true_anomaly):.3e}
            """
        else:
            result = "Planet not found."

    return render_template('index.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)

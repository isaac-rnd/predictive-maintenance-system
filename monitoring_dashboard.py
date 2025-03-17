import sys
import json
import paho.mqtt.client as mqtt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QGroupBox
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import collections

class SensorDataApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        # Initialize sensor data with limited buffer size for real-time plotting
        self.buffer_size = 100  # Limit the data to the latest 100 readings
        self.sensor_data = {
            'engine_rpm': collections.deque([0] * self.buffer_size, maxlen=self.buffer_size),
            'lub_oil_pressure': collections.deque([0.0] * self.buffer_size, maxlen=self.buffer_size),
            'coolant_temp': collections.deque([0.0] * self.buffer_size, maxlen=self.buffer_size),
        }

        self.client = mqtt.Client()
        self.client.username_pw_set("isaac", "isaac")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)
        self.client.loop_start()

        # Initialize previous values for smooth transitions
        self.prev_values = {
            'engine_rpm': 0,
            'lub_oil_pressure': 0.0,
            'coolant_temp': 0.0,
        }

    def initUI(self):
        # Set up the layout
        self.layout = QVBoxLayout()

        # Labels for real-time data
        self.rpm_label = QLabel("Engine RPM: 0")
        self.lub_oil_pressure_label = QLabel("Lubrication Oil Pressure: 0.0")
        self.coolant_temp_label = QLabel("Coolant Temperature: 0.0")

        # Add labels to layout
        self.layout.addWidget(self.rpm_label)
        self.layout.addWidget(self.lub_oil_pressure_label)
        self.layout.addWidget(self.coolant_temp_label)

        # Create graph widgets
        self.graph_layout = QHBoxLayout()
        self.engine_rpm_plot = pg.PlotWidget(title="Engine RPM")
        self.lub_oil_pressure_plot = pg.PlotWidget(title="Lub Oil Pressure")

        # Adding the graph widgets to the layout
        self.graph_layout.addWidget(self.engine_rpm_plot)
        self.graph_layout.addWidget(self.lub_oil_pressure_plot)
        self.layout.addLayout(self.graph_layout)

        # Set the layout
        self.setLayout(self.layout)
        self.setWindowTitle('Engine Sensor Data Monitor')
        self.show()

        # Timer for UI update
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)  # Update every 100 milliseconds

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT broker with result code " + str(rc))
        client.subscribe("maintainence")

    def on_message(self, client, userdata, msg):
        data = json.loads(msg.payload.decode())
        
        # Update sensor data buffer with new values
        self.sensor_data['engine_rpm'].append(data['engine_rpm'])
        self.sensor_data['lub_oil_pressure'].append(data['lub_oil_pressure'])
        self.sensor_data['coolant_temp'].append(data['coolant_temp'])

        # Store the previous values for transition effects
        self.prev_values['engine_rpm'] = self.sensor_data['engine_rpm'][-2] if len(self.sensor_data['engine_rpm']) > 1 else data['engine_rpm']
        self.prev_values['lub_oil_pressure'] = self.sensor_data['lub_oil_pressure'][-2] if len(self.sensor_data['lub_oil_pressure']) > 1 else data['lub_oil_pressure']
        self.prev_values['coolant_temp'] = self.sensor_data['coolant_temp'][-2] if len(self.sensor_data['coolant_temp']) > 1 else data['coolant_temp']

    def update_ui(self):
        # Update text labels
        self.rpm_label.setText(f"Engine RPM: {self.sensor_data['engine_rpm'][-1]}")
        self.lub_oil_pressure_label.setText(f"Lubrication Oil Pressure: {self.sensor_data['lub_oil_pressure'][-1]}")
        self.coolant_temp_label.setText(f"Coolant Temperature: {self.sensor_data['coolant_temp'][-1]}")

        # Update real-time graphs
        self.update_graph(self.engine_rpm_plot, self.sensor_data['engine_rpm'], self.prev_values['engine_rpm'], "Engine RPM", 'r')
        self.update_graph(self.lub_oil_pressure_plot, self.sensor_data['lub_oil_pressure'], self.prev_values['lub_oil_pressure'], "Lub Oil Pressure", 'b')

    def update_graph(self, plot_widget, data, prev_value, title, color):
        current_value = data[-1]
        
        # Create x values corresponding to the current data length
        x = list(range(len(data)))

        y = list(data)  # Current values only, as we want the latest data
        plot_widget.clear()
        plot_widget.plot(x, y, pen=pg.mkPen(color=color, width=2), name=title)
        plot_widget.setRange(xRange=[0, self.buffer_size], yRange=[min(data) - 5, max(data) + 5])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SensorDataApp()
    sys.exit(app.exec_())

import alert_user

insights = """
Here is an analysis of the provided engine sensor data:
## Overview:
The engine is operating at a relatively high RPM of 1345, and the coolant temperature is notably
high at 113.45 °C, indicating potential overheating concerns.
## Potential Issues:
The significant temperature difference between coolant and oil temperatures suggests a possible
issue with the engine's cooling system, which could cause overheating. Continued operation in this
state may lead to expedited wear and damage. There is also concern that some pressure levels are
out of the optimal range, particularly fuel pressure, which can affect performance and fuel economy.
## Maintenance Suggestions:
1. Perform a thorough cooling system inspection: Check the coolant level, hoses, and radiator for
any leaks, blockages, or corrosion, and conduct a coolant flush if necessary.
2. Pressure adjustments: Refer to the manufacturer's guidelines for calibration settings for the
lubrication oil pressure, fuel pressure, and coolant pressure, ensuring these are operating at optimal
levels to prevent unnecessary wear and tear on the engine. 
"""

# alert_user.alert_user(insights)
alert_user.show_warning_and_report(insights)
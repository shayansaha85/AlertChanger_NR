#!/bin/bash

# Run disable_alerts.py in the background
python3 disable_alerts.py &

# Run enable_alerts.py in the background
python3 enable_alerts.py &

# Wait for both background processes to finish
wait

echo "Both commands have finished executing."

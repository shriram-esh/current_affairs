#!/bin/bash

# Step 1: Run npm build to bundle chart.js files into one
npm run build

# Step 2: Start the Flask Server
flask run
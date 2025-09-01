#!/bin/bash

echo "🌊 Launching Marine Weather Dashboard..."
echo "======================================"
echo ""
echo "The dashboard will open in your default web browser."
echo "If it doesn't open automatically, go to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the dashboard when you're done."
echo ""

# Launch the dashboard
streamlit run dashboard.py --server.port 8501 --server.address localhost

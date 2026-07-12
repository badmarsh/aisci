#!/bin/bash
export XLA_PYTHON_CLIENT_PREALLOCATE=false

echo "Starting bgbw_fit.py on GPU..."
/usr/bin/time -f "bgbw_fit.py GPU time: %E (real)" python libs/physics-core/src/bgbw_fit.py --run-dir research/robert/runs/$(date +%Y-%m-%d)-bgbw-gls-gpu --cov-mode correlated --xi 1.0 > bgbw_fit_gpu.log 2>&1 &
PID1=$!

echo "Starting bgbw_profile_scan.py on GPU..."
/usr/bin/time -f "bgbw_profile_scan.py GPU time: %E (real)" python deployment/helper/bgbw_profile_scan.py --run-dir research/robert/runs/$(date +%Y-%m-%d)-bgbw-profile-scan-gpu --data-path libs/physics-core/data/fit_input_ins1735345.csv > bgbw_profile_scan_gpu.log 2>&1 &
PID2=$!

echo "Waiting for both GPU jobs to finish..."
wait $PID1
echo "bgbw_fit.py finished."

wait $PID2
echo "bgbw_profile_scan.py finished."
echo "Parallel GPU runs completed."

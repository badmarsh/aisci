#!/bin/bash

# test_fits_api.sh
echo "Testing /fits endpoint..."
curl -s -X GET "http://localhost:8001/api/projects/robert-boson-manuscript/fits" | grep -q "fitRows"
if [ $? -eq 0 ]; then
    echo "✅ /fits returned JSON with fitRows"
else
    echo "❌ /fits failed or did not return fitRows"
    exit 1
fi

echo "Testing /anomalies endpoint..."
curl -s -X GET "http://localhost:8001/api/projects/robert-boson-manuscript/anomalies" | grep -q "bin"
if [ $? -eq 0 ]; then
    echo "✅ /anomalies returned JSON array of anomalies"
else
    # It might return an empty array [] if there are no anomalies
    res=$(curl -s -X GET "http://localhost:8001/api/projects/robert-boson-manuscript/anomalies")
    if [[ "$res" == "[]" ]]; then
        echo "✅ /anomalies returned empty JSON array (no anomalies found)"
    else
        echo "❌ /anomalies failed or returned unexpected response: $res"
        exit 1
    fi
fi

echo "All tests passed!"

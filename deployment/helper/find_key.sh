#!/bin/bash
find /proc -maxdepth 2 -name environ -user ubuntu 2>/dev/null | while read -r env_file; do
    if grep -za "BRAVE_API_KEY" "$env_file" >/dev/null 2>&1; then
        echo "Found in $env_file:"
        tr '\0' '\n' < "$env_file" | grep "BRAVE_API_KEY"
    fi
done

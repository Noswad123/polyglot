#!/usr/bin/env bash

# put each example in a function
#

# Declare and populate the associative array
declare -A conf=(
  [host]="localhost"
  [port]="5432"
  [user]="admin"
  [password]="secret"
)

# Loop over the keys and print key=value pairs
for key in "${!conf[@]}"; do
  echo "$key=${conf[$key]}"
done


echo "line with \\ backslash" | read var

echo "var: $var"

#!/bin/bash

results_dir="results/confluence/"

export base_line=$(realpath ./results/confluence/baseline)
export latest_dir=$(realpath "$(ls -td -- ./results/confluence/*/ | head -n 1)")

echo $base_line
echo $latest_dir

yq -Y --indentless '.runs[0].fullPath="'"$base_line"'" | .runs[1].fullPath="'"$latest_dir"'"' ./reports_generation/performance_profile-orig.yml >  ./reports_generation/performance_profile.yml

cd reports_generation
python csv_chart_generator.py performance_profile.yml
cd ..



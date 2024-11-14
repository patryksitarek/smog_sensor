#!/bin/bash
source /home/sitar/miniconda3/etc/profile.d/conda.sh
conda activate smog_data_collection
python /home/sitar/smog/mqtt_collect_smog_data.py >> /home/sitar/smog/log.txt 2>&1

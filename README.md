# Smog Sensor Data Collector

Welcome to the Smog Sensor Data Collector repository! This project is prepared to collect data from smog sensors through MQTT (Message Queuing Telemetry Transport) protocol. This tool is essential for monitoring air quality and ensuring a healthy environment.

Prerequisites:
- Smog sensors publish data through MQTT under smog/sensor0 and smog/sensor1 topics
- MQTT broker already used (on the same device as the collection script)

# Set up script

### Conda environment
Create conda environment from environment.yml file
```
conda env create -f environment.yml
```

### Create service
Add /etc/systemd/system/smog_data_collection.service file
```
[Unit]
Description=Smog Data Collection Service
After=network.target

[Service]
Type=simple
ExecStart=/home/sitar/smog/run_mqtt_collect_smog_data.sh
Restart=always
User=sitar
WorkingDirectory=/home/sitar/smog

[Install]
WantedBy=multi-user.target
```

### Start service
```
systemctl daemon-reload
systemctl enable smog_data_collection.service
systemctl start smog_data_collection.service
```

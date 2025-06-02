# Running the app as a service in Raspberry Pi OS

# Deploying the application

Download the latest release of the .deb package from the repository: https://github.com/oscarrenalias/ai-agent-vision/releases

```bash
wget https://github.com/oscarrenalias/ai-agent-vision/releases/download/release-0.1.0-ci20250602172918.086f521/ai-agent-vision_0.1.0.ci20250602172918.086f521_arm64.deb

apt-get install ./ai-agent-vision_0.1.0.ci20250602172918.086f521_arm64.deb
```

# Application location

The application is installed under /opt/ai-agent-vision, with the following folders:

- conf: location of the env file that contains the configuration keys and values for the application
- data: location of the Mongo data files; mounted as a volume into the Mongo container
- uploads: location of all file uploads; mounted as a volume into the backend container, can be configured in the env file but that's not recommended
- backup: location of Mongo backups created by the mongo-backup container, which run every day at 2am

# Services

The appication is deployed as a system service so that it's automatically started and stopped together with the system. The service file is under `/etc/systemd/system/ai-agent-vision.service`, and can be operated as follows:

```bash
# reload the system service if changes are made
sudo systemctl daemon-reload

# enable the service (use "disable" for the opposite effect)
sudo systemctl enable ai-agent-vision

# start the service (or stop)
sudo systemctl start ai-agent-vision
```

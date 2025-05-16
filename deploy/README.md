## Running the app as a service in Raspbian

1. Copy file `ai-agent-vision.service` to `/etc/systemd/system/`:

```bash
sudo cp ai-agent-vision.service /etc/systemd/system/
```

Alternatively, it can be linked from the project's source code:

```bash
cd /etc/systemd/system && sudo ln -s /home/admin/ai-agent-vision/deploy/ai-agent-vision.service .
```

2. Download the docker-compose.release.yml file from the latest GitHub release: [GitHub Releases](https://github.com/oscarrenalias/ai-agent-vision/releases)

The file should be stored in `/root/ai-agent-vision/docker-compose.release.yml`. If a different location or filename should be used, update both the file path in the systemd service file and ensure the file is present at that location.

3. Create a configuration file for the application, use `backend/.env.example`as a template. Place it in the same location as the `docker-compose.release.yml` file:

```bash
cp ../backend/.env.example .env
```

Adapt accordingly.

4. Edit `docker-compose.release.yml`:

```bash
xxx
```

At this point, you can test the entire setup with docker-compose:

```bash
docker-compose -f docker-compose.release.yml up
```

Container logs will be printed to the standard output, errors and issues should be easy to spot.

5. Reload systemd, enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-agent-vision
sudo systemctl start ai-agent-vision
```

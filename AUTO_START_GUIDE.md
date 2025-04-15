# Docker Auto-Start Configuration Guide

## Docker Desktop Auto-Start on Windows

1. Open Docker Desktop
2. Click the gear icon (⚙️) in the top-right corner to open Settings
3. Go to "General" settings
4. Check the option "Start Docker Desktop when you log in"
5. Click "Apply & Restart"

## To Test Auto-Start

1. Restart your computer
2. Docker Desktop should start automatically
3. Your application container should be automatically started based on the `restart: unless-stopped` policy

## Checking Container Status

```
docker ps
```

This command will show if your container is running.

## Manually Starting the Service

If needed, you can start the service manually with:

```
cd d:\Stocks\volume_capture
docker-compose up -d
```

The `-d` flag runs it in detached mode (background).

## Viewing Logs

To view the logs of your running container:

```
docker-compose logs -f
```

The `-f` flag follows the log output in real-time.

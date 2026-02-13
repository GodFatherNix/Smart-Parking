# SmartPark System Architecture Diagram

```text
                 +---------------------+
                 |  Camera Streams     |
                 |  (RTSP / MP4)       |
                 +----------+----------+
                            |
                            v
                 +---------------------+
                 | Vision Service      |
                 | YOLO + ByteTrack    |
                 | Line Crossing       |
                 +----------+----------+
                            |
                            | POST /event
                            v
 +--------------------------+---------------------------+
 | Backend API (FastAPI)                                |
 | - /event /floors /recommend /events                  |
 | - /health /health/live /health/ready                 |
 | - /monitoring/metrics /monitoring/alerts             |
 +--------------------------+---------------------------+
                            |
                            v
                 +---------------------+
                 | PostgreSQL / SQLite |
                 | Floors + Events     |
                 +---------------------+
                            ^
                            |
                 +----------+----------+
                 | Frontend Dashboard  |
                 | React + Vite        |
                 +---------------------+

Ops Plane:
- GitHub Actions CI/CD
- Render deployment hooks
- Fluent Bit log aggregation
- Scheduled PostgreSQL backups
```

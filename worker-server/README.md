# Worker Server for Cryptocurrency Updates

This server runs a scheduled background job to trigger cryptocurrency data updates every 15 minutes via a NATS event queue.

## Features

- Scheduled job that runs every 15 minutes
- Publishes events to NATS to trigger updates in the API server

## Prerequisites

- Node.js (v16 or higher)
- NATS server

## Setup

1. Clone the repository
2. Navigate to the worker-server directory:
   ```
   cd worker-server
   ```
3. Install dependencies:
   ```
   npm install
   ```
4. Create a `.env` file based on `.env.example` and fill in your configuration
5. Start the server:
   ```
   npm start
   ```
   For development with auto-reload:
   ```
   npm run dev
   ```

## Environment Variables

Create a `.env` file with the following variables:

```
PORT=3001
NATS_URL=nats://localhost:4222
CRON_SCHEDULE="*/15 * * * *"
```

## Architecture

The worker server consists of the following components:

- Scheduler that uses node-cron to run tasks at specified intervals
- NATS service for publishing events

## Running with Docker

```bash
docker build -t worker-server .
docker run -p 3001:3001 --env-file .env worker-server
```
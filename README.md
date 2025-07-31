# 📨 async_task_queue_monitor

An asynchronous demo task queue system using **RabbitMQ** and **aio-pika**.

## 📌 Overview

This project simulates a distributed task processing pipeline:

- `producer` — generates random tasks (`wait`, `ping`, `fail`)
- `worker` — processes tasks from the queue
- `monitor` — listens for results and logs them

Components communicate via RabbitMQ using the AMQP protocol with the `aio-pika` async client.

---

## 🏗️ Architecture

```text
 ┌──────────┐      ┌────────────┐      ┌──────────────┐
 │ Producer ├─────► Task Queue ├─────►│    Worker     │
 └──────────┘      └────────────┘     └──────┬───────┬┘
                                             │       │
                                      ┌──────▼────┐┌─▼─────────┐
                                      │ Result MQ ││ Dead Queue│ (optional)
                                      └──────┬────┘└───────────┘
                                             │
                                        ┌────▼────┐
                                        │ Monitor │
                                        └─────────┘

---

## 🚀 Quick Start

### 1. Clone the project

```bash
git clone https://github.com/peckerw00d/async_task_queue_monitor.git
cd async_task_queue_monitor
```

### 2. Run with Docker Compose

```bash
docker compose up --build
```

* **RabbitMQ Web UI:** [http://localhost:15672](http://localhost:15672)
  Username: `rmuser`
  Password: `rmpassword`

---

## ⚙️ Environment Variables

You can optionally create a `.env` file:

```env
RABBITMQ_URL=amqp://rmuser:rmpassword@rabbitmq:5672/
RABBITMQ_DEFAULT_USER=rmuser
RABBITMQ_DEFAULT_PASS=rmpassword
```

> Default values are already provided in `docker-compose.yaml`, so this is optional.

---

## 👨‍💻 Run Locally (without Docker)

Make sure RabbitMQ is running on `localhost:5672`:

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

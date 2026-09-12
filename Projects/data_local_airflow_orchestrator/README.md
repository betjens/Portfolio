# Demo - Working with Airflow Locally

This demo will show you how to get a start using airflow, DAGs. Before hand I
have installed `Visual Studio Code` as my code editor.

Pasos:

## Instalación de entorno de trabajo

1. Create a folder project. ie: `demo`
2. run:

```
wsl --install
```
3. In WSL, run:

```
sudo apt update
sudo apt upgrade -y
```
4. Verify python version
```
# got ... Python 3.12.3
python3 --version
```
5. Install an additional library to be able to create virtual enviroments.
```
sudo apt install python3-venv python3-pip -y
```
6. Create a directory workspace. ie: `airflow-demo`
```
mkdir ~/airflow-demo
cd ~/airflow-demo
```
7. Create and activate our virtual environment.
```
# create venv named venv
python3 -m venv .venv
# activate venv
source .venv/bin/activate
```
> Note: Airflow Demo will be running in Linux with Python.

## Airflow local

In your WSL Python Virtual enviroment ( As indicated in the previous step) run:

```
# I got python version 3.12 and looking to install the
# latest airflow version available at this time `3.3.1`
pip install "apache-airflow==3.3.1" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.3.1/constraints-3.12.txt"
```

To run airflow, ran:

```
airflow standalone
```

This should make you able to see airflow running in `http://localhost:8080`.

1. In a new terminal, ran `wsl` to get a new virtual terminal.
2. Go to your airflow directory. Usually it should be found in
`/home/<account>/airflow` and peek the authentication file generated.
```
cat simple_auth_manager_passwords.json.generated
# This should provide you with the credentials to access to airflow interface.
```

To stop airflow, in the terminal running airflow just press `ctrl+c`.

## Additional Details

### How much can a local Airflow server handle?

While learning Airflow, a common question is how powerful the machine running Airflow needs to be.

For example, suppose I am learning Airflow and have an older PC available that I can dedicate as a local server:

* **CPU:** Intel Core i7
* **RAM:** 12 GB
* **Storage:** SSD
* **OS:** Linux / Ubuntu
* **Purpose:** Dedicated Airflow server

For learning, personal projects, home labs, and even relatively small workloads, this is already a capable machine.

Airflow itself is primarily an **orchestrator**. The amount of resources required depends less on the number of DAGs and more on what the tasks actually do and how many tasks execute concurrently.

For example, a task that sends a query to BigQuery:

```text
Airflow Task
     │
     ▼
  BigQuery
     │
     ▼
Processing happens in GCP
```

may consume very few resources on the Airflow server.

On the other hand:

```text
Airflow Task
     │
     ▼
Read 20 GB CSV
     │
     ▼
Process with Pandas
     │
     ▼
CPU + RAM used locally
```

can consume significant resources because the actual processing happens on the Airflow machine.

### Approximate capacity

A 12 GB RAM / Core i7 server should comfortably handle a learning environment with tens of DAGs.

A rough guideline could be:

| Workload                    | Expected result                            |
| --------------------------- | ------------------------------------------ |
| 10–30 simple DAGs           | Very comfortable                           |
| 50–100 moderate DAGs        | Usually manageable                         |
| 100+ lightweight DAGs       | Possible with proper configuration         |
| Many heavy concurrent tasks | CPU/RAM may become the bottleneck          |
| Large Pandas / ML workloads | Better executed outside the Airflow server |

The number of DAGs alone does **not** determine how much hardware Airflow needs.

For example:

```text
500 DAGs
running occasionally
with lightweight tasks

        may require fewer resources than

10 DAGs
running constantly
processing several GB locally
```

### RAM considerations

From 12 GB of available RAM, part of it will be consumed by the operating system and Airflow components.

A simplified example:

```text
12 GB RAM

Operating System             ~1–2 GB
Airflow + Database            ~2–3 GB
Safety margin                 ~2 GB
------------------------------------
Available for tasks           ~5–7 GB
```

The actual numbers will vary, but this provides a useful mental model.

Task resource consumption can also vary significantly:

```text
Light Python task          ~100–300 MB
Medium Pandas task         ~500 MB–1.5 GB
Heavy processing task      ~2–4+ GB
```

Therefore, controlling **task concurrency** is important.

For a small local server, it is better to start conservatively and increase concurrency after observing CPU and memory usage.

For example:

```ini
parallelism = 8
max_active_tasks_per_dag = 4
```

For CPU-intensive workloads, a smaller value such as 4–6 concurrent tasks may be more appropriate.

For I/O-heavy workloads—API requests, database queries, file transfers, BigQuery jobs, etc.—the server may be able to handle more concurrent tasks because most of the processing happens elsewhere.


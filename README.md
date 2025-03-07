# Real-Time Stock Data Streaming & Visualization Pipeline on GCP

This repository demonstrates an **end-to-end** pipeline for **real-time ingestion, processing, and visualization** of stock market data on **Google Cloud Platform** (GCP). It integrates multiple GCP services (Cloud Run, Pub/Sub, Dataflow, BigQuery, Cloud Composer) along with Terraform for infrastructure as code and Power BI for interactive analytics.

---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Technologies & Where They Are Used](#technologies--where-they-are-used)  
3. [Workflow & Scheduling](#workflow--scheduling)  
4. [Deployment Evolution](#deployment-evolution)  
5. [Power BI Dashboard & DAG Screenshot](#power-bi-dashboard--dag-screenshot)
6. [Conclusion](#conclusion)

---

## Project Overview

- **Goal:** Provide **near real-time** data on live stock quotes and company information, enabling minute-level insights.  
- **Key Components:**  
  - **Data Ingestion:** Cloud Run Jobs push data to Pub/Sub.  
  - **Processing:** Dataflow reads messages from Pub/Sub and writes raw data as text files to a Cloud Storage bucket.  
  - **Analytics & Visualization:** BigQuery ingests these raw files from Cloud Storage(Bucket) for further transformation and then loads as BigQuery Tables used for  Power BI dashboards.  
  - **Orchestration:** Airflow (via Cloud Composer) triggers Cloud Run Jobs on a set schedule, controlling when new data is ingested and processed. Big Query transformations are also scheduled in sync with new data ingestions using scheduled notebooks.

---

## Technologies & Where They Are Used

1. **Cloud Run**  
   - **Usage:** Hosts containerized Python scripts for two separate tasks:  
     1. **Stock quotes** (run every 10 minutes during market hours).  
     2. **Company info** (run once daily at a specific time).  
   - **Benefit:** Serverless, auto-scaling environment that reduces idle costs compared to a persistent cluster.

2. **Pub/Sub**  
   - **Usage:** Acts as the messaging layer where the Cloud Run scripts publish data. Pub/Sub then listens to these messages for downstream processing.

3. **Dataflow**  
   - **Usage:** Reads messages from Pub/Sub and writes them as text files to a **raw-data** bucket in Cloud Storage.  
   - **Why:** This decouples ingestion from analytics, storing raw data for reliability and potential reprocessing.

4. **Cloud Storage (GCP Bucket)**  
   - **Usage:** Stores raw text files (output from Dataflow). BigQuery later performs transformations and ingests these files into structured tables.

5. **BigQuery**  
   - **Usage:** Loads raw text files from Cloud Storage, transforms them as needed, and serves as the data warehouse for analytics. Power BI queries these tables for near real-time dashboarding.

6. **Cloud Composer (Airflow)**  
   - **Usage:** Orchestrates the pipeline schedules and triggers (Cloud Run jobs).  
   - **Local Testing:** DAGs were first tested locally using Airflow within Docker containers and later transitioned to Cloud Composer for the operational phase.

7. **Terraform**  
   - **Usage:** Infrastructure as code to provision GCP services such as Pub/Sub topics, Cloud Storage buckets, and BigQuery.  
   - **Ensures** consistent, repeatable deployments under version control.

8. **Docker**  
   - **Usage:** Containerizes the Python scripts for seamless deployment on Cloud Run (and earlier testing on GKE).  
   - **Advantage:** Consistent runtime environment, quicker iteration cycles.

9. **Security & Best Practices**  
   - **Credentials Management:** Uses Workload Identity (on GKE) and Cloud Secret Manager for sensitive keys in production.  
   - **IAM Roles:** Minimally scoped (e.g., `pubsub.publisher`, `secretmanager.secretAccessor`) to limit access as needed.

---

## Workflow & Scheduling

### **Company Info Job**
- **Runs Once Daily:**  
  - **Schedule:** 10:00 AM (Monday–Friday), or a small time window around 10:00 AM ET.  
  - **Data Flow:** Publishes new company data (market cap, IPO details, etc.) to Pub/Sub → Dataflow writes to Cloud Storage (raw text) → BigQuery ingests.

### **Stock Quotes Job**
- **Runs Every 10 Minutes (9:30 AM–4:00 PM ET)**  
  - **Reason:** Provides minute-level insights while limiting cost.  
  - **Data Flow:** Publishes stock prices to Pub/Sub → Dataflow writes to Cloud Storage → BigQuery transforms and loads the data for real-time analytics.

### **Local Dev → Cloud Composer**
- **Testing Locally:**  
  - Airflow in Docker verifies that tasks branch correctly for daily vs. frequent jobs.  
  - Scripts are containerized to confirm Docker images run as expected.
- **Production in Cloud Composer:**  
  - Schedules, triggers, and monitors the two Cloud Run jobs at their respective times.  

---

## Deployment Evolution

1. **Initial GKE Testing:**  
   - Python scripts deployed on a GKE Autopilot cluster to validate the orchestration approach with containerized services.  

2. **Migration to Cloud Run Jobs:**  
   - **Cost Optimization:** Transitioned from GKE to Cloud Run’s serverless model,significantly reducing idle running costs.  
   - Orchestrated by Airflow/Cloud Composer to coordinate daily vs. frequent tasks.

---

## Power BI Dashboard & DAG Screenshot


- **Dashboard Video**
  
  [![Demo Video]](https://github.com/user-attachments/assets/34748bb6-7358-4bb3-9668-f715a72579fd)  


- **Airflow DAG Screenshot**  
    
    ![DAG Screenshot 1](https://github.com/dsp196/Stock_Data_Streaming_GCP/blob/main/assets/Dag.png)  
  


---

## Conclusion

By combining **Cloud Run** for containerized scripts, **Pub/Sub** for messaging, **Dataflow** for ingesting raw text file into Cloud Storage, **BigQuery** for warehousing data and **Power BI** for dashboarding, this pipeline ensures:

- **Near Real-Time Data:** Frequent updates of both stock prices and company information, easily visualized in **Power BI**.  
- **Cost Efficiency:** Serverless approach with Cloud Run and minimal overhead (auto-scaling, no idle cluster).  
- **Security & Best Practices:** Credential management via Cloud Secret Manager, minimal IAM roles, and optional Workload Identity.  
- **Infrastructure as Code:** Terraform fosters reproducible, maintainable deployments.  
- **Scalable Orchestration:** Airflow (Cloud Composer) handles scheduling and branching logic, tested locally before going live.


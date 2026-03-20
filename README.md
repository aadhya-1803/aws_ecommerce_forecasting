# AWS E-Commerce Analytics & Forecasting Pipeline

An end-to-end serverless data pipeline built on AWS that ingests, transforms, and analyzes e-commerce transactions with a time series forecasting model to predict future revenue trends.
# What This Project Does
This project simulates what a real data team does at an e-commerce company taking raw transactional data, cleaning it up, running SQL analytics on it, visualizing it on a dashboard, and using machine learning to forecast where revenue is headed.
Everything runs on AWS using serverless architecture, which means no servers to manage, no infrastructure headaches, and it scales automatically. The entire pipeline is automated drop a file into S3 and the rest happens on its own.
# Tech Stack
1. Data Generation- Python, Faker, boto3
2. Cloud Storage- AWS S3
3. ETL / Transformation- AWS Lambda, Pandas
4. Analytics - Amazon Athena (SQL)
5. Visualization - Looker Studio
6. Forecasting - Facebook Prophet
7. Environment - VS Code, Google Colab

# Key Features
1. Automated ETL Pipeline
Raw CSV files dropped into S3 automatically trigger a Lambda function that cleans the data, removes cancelled orders, adds derived columns like revenue band, estimated profit, day of week, and weekend flag then writes the transformed data back to a separate S3 location.

2. SQL Analytics with Athena
Amazon Athena queries the transformed data directly from S3 so no database server needed. Business questions answered include top revenue cities, best selling categories, payment method distribution, and weekend vs weekday performance.

3. Interactive Dashboard
A Looker Studio dashboard connects to the Athena data and presents five visualizations along with three KPI scorecards showing total revenue, total orders, and average order value.

4. Revenue Forecasting Model
A Facebook Prophet model trained on historical daily revenue data forecasts the next 30 days of revenue. The model captures weekly seasonality patterns and overall trend direction. Predictions are saved back to S3 for traceability.

# Analytics Results
These are sample insights from the pipeline:
Top Revenue City -  Visakhapatnam
Best Category - Home & Kitchen (31.1%)
Most Used Payment - Evenly distributed across UPI, Cards, COD
Revenue Band - Premium orders drive 60%+ of total revenue
Weekend vs Weekday - Weekend orders show higher average order value

# A Note on the Forecasting Model
The forecasting model is trained on 30 days of historical daily revenue data which is on the lower end for time series forecasting. Ideally, Prophet performs best with at least 1-2 years of data to detect yearly seasonality and longer term trends.
In this project, 30 days was a deliberate constraint as the goal was to demonstrate the full ML workflow end to end: 
aggregating transactional data into a time series, training a forecasting model, generating predictions with confidence intervals, and persisting results back to cloud storage.
In a real production environment, this same pipeline would simply accumulate data over time, and the model would be retrained periodically on the growing dataset improving in accuracy as more history becomes available. The architecture is already set up to support that.

# Dashboard
<img width="600" height="430" alt="image" src="https://github.com/user-attachments/assets/48d27557-4146-4f28-a47e-72c4cb1017b0" />

# What I Learned
Building this project gave me hands-on experience with how data actually moves in a cloud environment from raw ingestion all the way to a business dashboard and predictive model. The most interesting challenge was understanding how AWS IAM permissions work across services and how serverless functions like Lambda can replace traditional ETL scripts running on scheduled servers.
The forecasting component introduced me to the practical constraints of time series modeling specifically how data volume and quality directly affect prediction reliability, which is something that's easy to overlook when working with clean tutorial datasets.

# Author
Aadhya- aadhya-1803

# This project is part of Alex the Analyst's bootcamp on YouTube. All the resources and most of the project are from this guidance 
- The YouTube channel link:- https://www.youtube.com/@AlexTheAnalyst
- the bootcamp link:- https://www.youtube.com/watch?v=rGx1QNdYzvs&list=PLUaB-1hjhk8FE_XZ87vPPSfHqb6OcM0cF

# Global Layoff Analysis: Trends & Funding Impact
This project explores global layoff events from 2020 onwards, analyzing patterns related to company funding, industry, and geographical location. Leveraging MySQL for data cleaning and initial analysis, and designed for showcasing data project skills.

# Project Overview
This repository contains the SQL scripts and relevant documentation for an in-depth analysis of worldwide layoffs. The primary goal is to uncover relationships between companies' raised funds and the scale or severity of their layoff events, while also identifying key trends across different industries and countries.

# Key Features
Data Acquisition & Staging: Initial setup and loading of raw layoff data into a MySQL staging environment.
Comprehensive Data Cleaning: Robust SQL-based methods for handling duplicates, standardizing text fields (company, industry, country), and ensuring correct data types (especially for dates).
In-depth MySQL Analysis: Utilizes advanced SQL queries for:
Analyzing layoff magnitude and percentage against funding tiers.
Identifying top companies and industries by total layoffs.
Examining yearly, monthly, and stage-specific layoff trends.
Investigating funding distribution and its correlation with layoffs across industries and countries.
Reproducible Code: All cleaning and analysis steps are documented with clear SQL scripts.

# Methodology
The project follows a standard data analysis pipeline:

Data Ingestion: Raw layoff data was loaded into a MySQL database.
Data Cleaning & Transformation: All preprocessing (duplicate removal, standardization, null handling) was performed using a series of SQL UPDATE, DELETE, and ALTER TABLE statements to ensure data quality.
Exploratory Data Analysis (EDA): Initial trends and aggregates were derived using SQL queries to understand the dataset's characteristics.
Targeted Analysis: Specific analytical questions regarding funding impact, industry performance, and temporal trends were addressed with complex SQL queries, including CTEs and window functions.

# Technologies Used
MySQL: Primary database for data storage, cleaning, and analysis.

# Key Findings
- The highest country to have layoff events is the United States, which is 713 events and 256,474 in total labour recorded 
- also the highest country to have fundraising in amount is the United States for 675,871
- the highest industries to have layoffs is consumer, retail in order 46,682 and 43,613 for each 
- The highest year in layoff is 2023
- there is direct corrolation between raising funds and companies lay off increased

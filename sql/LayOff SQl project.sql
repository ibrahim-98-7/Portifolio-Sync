/*
Project: Global Layoff Analysis - Full MySQL Script
Author: Ibrahim Abdleazeam

Description:
    This script contains all the SQL code for the Global Layoff Analysis project.
    It covers:
    1.  Initial table creation and data loading from the raw 'layoffs' table.
    2.  Comprehensive data cleaning, including duplicate removal and standardization.
    3.  In-depth analysis of layoff trends by company, industry, country, and time.
    4.  Specific analysis on the impact of company funding on layoff events.

    IMPORTANT: After the duplicate removal step (Section 2), it's assumed you will
    rename 'layoffs_stagging_copy' back to 'layoffs_stagging' or work consistently
    with 'layoffs_stagging_copy' throughout the rest of the script. The analysis
    sections below use 'layoffs_stagging'.
*/

-- -------------------------------------------------------------------
--  1. Data Preparation: Staging Table Creation & Initial Load
-- -------------------------------------------------------------------
-- Create a staging table 'layoffs_stagging' with the same structure as the raw 'layoffs' table.
-- This keeps your raw data safe and untouched.
CREATE TABLE layoffs_stagging LIKE layoffs;

-- Load all raw data into our new staging table.
INSERT INTO layoffs_stagging
SELECT *
FROM layoffs;

-- Quick check to ensure data loaded correctly.
SELECT *
FROM layoffs_stagging LIMIT 10;

-- -------------------------------------------------------------------
--  2. Data Cleaning: Duplicate Removal
-- -------------------------------------------------------------------
-- We first identify duplicate rows. A row is considered a duplicate if all its columns
-- are identical. We assign a row number to help spot them.
WITH duplicate_cte AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY company, location, industry, total_laid_off, percentage_laid_off, `date`, stage, country, funds_raised_millions
        ) AS row_num
    FROM
        layoffs_stagging
)
-- Display the identified duplicates (rows with row_num > 1).
SELECT *
FROM duplicate_cte
WHERE row_num > 1;

-- To safely remove duplicates, we'll create a temporary copy of our staging table,
-- insert only the unique records, and then clean up.
CREATE TABLE `layoffs_stagging_copy` (
    `company` TEXT, `location` TEXT, `industry` TEXT, `total_laid_off` INT DEFAULT NULL,
    `percentage_laid_off` TEXT, `date` TEXT, `stage` TEXT, `country` TEXT,
    `funds_raised_millions` INT DEFAULT NULL, `row_num` INT -- Temporary column for duplicate handling
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

-- Populate the copy table, adding the row number for each record.
INSERT INTO layoffs_stagging_copy
SELECT
    *,
    ROW_NUMBER() OVER (
        PARTITION BY company, location, industry, total_laid_off, percentage_laid_off, `date`, stage, country, funds_raised_millions
    ) AS row_num
FROM
    layoffs_stagging;

-- Delete all duplicate records (where row_num > 1) from our copy.
DELETE FROM layoffs_stagging_copy
WHERE row_num > 1;

-- Now, you should drop the original 'layoffs_stagging' table and rename 'layoffs_stagging_copy'
-- to 'layoffs_stagging' to proceed with a clean, single staging table.
-- DROP TABLE layoffs_stagging;
-- ALTER TABLE layoffs_stagging_copy RENAME TO layoffs_stagging;

-- -------------------------------------------------------------------
--  3. Data Cleaning: Standardization and Type Conversion
-- -------------------------------------------------------------------
-- Remove any accidental leading/trailing spaces from company names for consistency.
UPDATE layoffs_stagging
SET company = TRIM(company);

-- Standardize industry names (e.g., group all 'crypto' variations under 'Crypto').
-- Check distinct industries first to find patterns.
SELECT DISTINCT industry FROM layoffs_stagging ORDER BY 1;
UPDATE layoffs_stagging
SET industry = 'Crypto'
WHERE industry LIKE 'Crypto%';
-- Add more UPDATE statements here for other industry inconsistencies you find (e.g., 'Finance' vs 'Financial').

-- Standardize country names (e.g., remove trailing periods from 'United States.').
-- Check distinct countries first.
SELECT DISTINCT country FROM layoffs_stagging ORDER BY 1;
UPDATE layoffs_stagging
SET country = TRIM(TRAILING '.' FROM country)
WHERE country LIKE 'United States%';

-- Convert the 'date' column from text to a proper DATE format.
-- First, update the column values using STR_TO_DATE.
UPDATE layoffs_stagging
SET `date` = STR_TO_DATE(`date`, '%m/%d/%Y');
-- Then, change the column's data type.
ALTER TABLE layoffs_stagging
MODIFY COLUMN `date` DATE;

-- -------------------------------------------------------------------
--  4. Data Cleaning: Handling Missing Values and Final Touches
-- -------------------------------------------------------------------
-- Identify records where 'industry' is missing or empty.
SELECT * FROM layoffs_stagging WHERE industry IS NULL OR industry = '';

-- Convert empty industry strings to NULL for easier handling.
UPDATE layoffs_stagging
SET industry = NULL
WHERE industry = '';

-- Attempt to fill in missing industry values by looking up other records for the same company.
-- This assumes a company generally stays in one industry.
UPDATE layoffs_stagging AS t1
JOIN layoffs_stagging AS t2
    ON t1.company = t2.company
SET t1.industry = t2.industry
WHERE (t1.industry IS NULL)
AND t2.industry IS NOT NULL;

-- Identify records where both 'total_laid_off' AND 'percentage_laid_off' are missing.
-- These rows don't provide core layoff data, so we'll remove them.
SELECT * FROM layoffs_stagging
WHERE total_laid_off IS NULL AND percentage_laid_off IS NULL;

-- Delete those irrelevant rows.
DELETE FROM layoffs_stagging
WHERE total_laid_off IS NULL AND percentage_laid_off IS NULL;

-- Finally, remove the temporary 'row_num' column used for duplicate identification.
ALTER TABLE layoffs_stagging
DROP COLUMN row_num;

-- Quick check on the first few rows of our cleaned data.
SELECT * FROM layoffs_stagging LIMIT 10;

-- -------------------------------------------------------------------
--  5. Analysis: Overview & Trends
-- -------------------------------------------------------------------
-- Find the largest layoff events (max total_laid_off and max percentage_laid_off).
SELECT MAX(total_laid_off) AS max_total_laid_off, MAX(percentage_laid_off) AS max_percentage_laid_off
FROM layoffs_stagging;

-- See companies that laid off 100% of their staff, ordered by total laid off.
SELECT *
FROM layoffs_stagging
WHERE percentage_laid_off = 1
ORDER BY total_laid_off DESC;

-- Total layoffs aggregated by company.
SELECT company, SUM(total_laid_off) AS total_layoffs
FROM layoffs_stagging
GROUP BY company
ORDER BY total_layoffs DESC;

-- Total layoffs aggregated by industry.
SELECT industry, SUM(total_laid_off) AS total_layoffs
FROM layoffs_stagging
WHERE industry IS NOT NULL
GROUP BY industry
ORDER BY total_layoffs DESC;

-- Total layoffs aggregated by country.
SELECT country, SUM(total_laid_off) AS total_layoffs
FROM layoffs_stagging
WHERE country IS NOT NULL
GROUP BY country
ORDER BY total_layoffs DESC;

-- Average percentage laid off by country.
SELECT country, AVG(percentage_laid_off) AS avg_percentage_layoff
FROM layoffs_stagging
WHERE country IS NOT NULL AND percentage_laid_off IS NOT NULL
GROUP BY country
ORDER BY avg_percentage_layoff DESC;

-- Total layoffs by year.
SELECT YEAR(`date`) AS layoff_year, SUM(total_laid_off) AS total_laid_off
FROM layoffs_stagging
WHERE `date` IS NOT NULL
GROUP BY layoff_year
ORDER BY layoff_year DESC;

-- Total layoffs by company stage (e.g., Series A, Public).
SELECT stage, SUM(total_laid_off) AS total_laid_off
FROM layoffs_stagging
WHERE stage IS NOT NULL
GROUP BY stage
ORDER BY stage ASC;

-- Monthly layoff trends with a rolling sum.
-- This helps visualize the cumulative impact over time.
WITH monthly_total AS (
    SELECT
        DATE_FORMAT(`date`, '%Y-%m') AS `month`,
        SUM(total_laid_off) AS laid_off_count
    FROM layoffs_stagging
    WHERE `date` IS NOT NULL
    GROUP BY `month`
    ORDER BY `month` ASC
)
SELECT `month`, laid_off_count, SUM(laid_off_count) OVER (ORDER BY `month`) AS rolling_total_laid_off
FROM monthly_total;

-- Top 5 companies by total layoffs each year.
-- This helps identify the biggest layoff events annually.
WITH company_by_year AS (
    SELECT company, YEAR(`date`) AS `year`, SUM(total_laid_off) AS total_layoff
    FROM layoffs_stagging
    WHERE `date` IS NOT NULL
    GROUP BY company, YEAR(`date`)
),
company_year_rank AS (
    SELECT *, DENSE_RANK() OVER (PARTITION BY `year` ORDER BY total_layoff DESC) AS `rank`
    FROM company_by_year
    WHERE `year` IS NOT NULL
)
SELECT *
FROM company_year_rank
WHERE `rank` <= 5
ORDER BY `year` DESC, `rank` ASC;

-- -------------------------------------------------------------------
--  6. Analysis: Funding Impact
-- -------------------------------------------------------------------
-- Overview of companies with reported funding, ordered by year and funds raised.
SELECT YEAR(`date`) AS `year`, industry, company, funds_raised_millions, percentage_laid_off, total_laid_off
FROM layoffs_stagging
WHERE funds_raised_millions IS NOT NULL AND industry IS NOT NULL
ORDER BY `year` DESC, funds_raised_millions DESC;

-- Average layoff metrics by funding tiers (Under $100M, $100M-$500M, Over $500M).
-- This explores how funding levels might correlate with layoff scale or severity.
SELECT
    CASE
        WHEN funds_raised_millions < 100 THEN 'Under $100M'
        WHEN funds_raised_millions >= 100 AND funds_raised_millions < 500 THEN '$100M - $500M'
        WHEN funds_raised_millions >= 500 THEN 'Over $500M'
        ELSE 'Unknown/Not Disclosed'
    END AS funding_tier,
    AVG(total_laid_off) AS avg_total_laid_off,
    AVG(percentage_laid_off) AS avg_percentage_laid_off,
    COUNT(*) AS number_of_layoff_events
FROM layoffs_stagging
WHERE total_laid_off IS NOT NULL AND percentage_laid_off IS NOT NULL AND funds_raised_millions IS NOT NULL
GROUP BY funding_tier
ORDER BY
    CASE
        WHEN funding_tier = 'Under $100M' THEN 1
        WHEN funding_tier = '$100M - $500M' THEN 2
        WHEN funding_tier = 'Over $500M' THEN 3
        ELSE 4
    END;

-- Industry-specific funding and layoff impact.
-- See which industries attract high funding and how their layoffs compare.
SELECT
    industry,
    AVG(funds_raised_millions) AS avg_funds_raised_millions,
    AVG(total_laid_off) AS avg_total_laid_off,
    AVG(percentage_laid_off) AS avg_percentage_laid_off,
    COUNT(*) AS number_of_layoff_events
FROM layoffs_stagging
WHERE industry IS NOT NULL AND funds_raised_millions IS NOT NULL
    AND total_laid_off IS NOT NULL AND percentage_laid_off IS NOT NULL
GROUP BY industry
ORDER BY avg_funds_raised_millions DESC;

-- Country-level funding and layoff trends.
-- Understand the overall funding and layoff situation in different countries.
SELECT
    country,
    SUM(funds_raised_millions) AS total_funds_raised_in_country,
    AVG(total_laid_off) AS avg_country_total_laid_off,
    AVG(percentage_laid_off) AS avg_country_percentage_laid_off,
    COUNT(*) AS number_of_layoff_events
FROM layoffs_stagging
WHERE country IS NOT NULL AND funds_raised_millions IS NOT NULL
    AND total_laid_off IS NOT NULL AND percentage_laid_off IS NOT NULL
GROUP BY country
ORDER BY total_funds_raised_in_country DESC;

/*
# Key Findings
- The highest country to have layoff events is the United States, which is 713 events and 256,474 in total labour recorded 
- also the highest country to have fundraising in amount is the United States for 675,871
- the highest industries to have layoffs is consumer, retail in order 46,682 and 43,613 for each 
- The highest year in layoff is 2023
- there is direct corrolation between raising funds and companies lay off increased
*/

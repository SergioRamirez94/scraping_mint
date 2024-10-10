# Scraping Mint Project

This project is a web scraping tool designed to extract and process data from specific sources, with a focus on energy supply metrics. It includes GitHub Actions for continuous deployment to AWS when code is pushed to the staging branch. The project is integrated with Google Drive for data storage and supports automatic uploading of PDFs and CSVs to designated folders.

## Table of Contents
- [Getting Started](#getting-started)
- [Running Locally](#running-locally)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Repository Link](#repository-link)

## Getting Started

To get a copy of the project up and running locally on your machine, follow these steps.

### Prerequisites

1. **Python**: Version 3.11.7
2. **Git**: For version control and cloning the repository
3. **Virtual Environment**: Optional but recommended for managing dependencies

### Cloning the Repository

1. Open your terminal.
2. Clone the repository:
   ```bash
   git clone https://github.com/SergioRamirez94/scraping-mint.git
   ```
4. Navigate to the project directory:
 ```bash
   cd scraping-mint
  ```
## Running Locally

### Step 1: Set up the Environment
1. **Create a Virtual Environment**:
  ```bash
   python3 -m venv venv
   ```
2. **Activate the Virtual Environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install the Dependencies**:
  ```bash
   pip install -r srs/requirements.txt
  ```
### Step 2: Configure Environment Variables
1. Create a `.env` file in the `srs` folder.
2. Add the following environment variables to the `.env` file:
   ```bash
   GOOGLE_DRIVE_FOLDER_PDF_ID=1E5BIkwG7thVKwkp9Y8Uu8pIvDlZupB5V
   GOOGLE_DRIVE_FOLDER_CSV_ID=1aLuf8TYB5Oym3zW86w1lcEP4T0J0L2_H
   ```
4. Place the `service_account.json` file in the `srs` folder to enable integration with Google Drive.

### Step 3: Run the Scraper
1. Navigate to the `srs` directory:
   ```bash
   cd srs
   ```
3. Run the Scrapy spider:
   ```bash
   scrapy crawl grid_spider
   ```

The scraper will now begin collecting data and uploading results to the specified Google Drive folders.

## Deployment

This project uses GitHub Actions to automate deployments to AWS. When you push code to the **staging** branch, GitHub Actions triggers the deployment process. AWS keys are stored securely as GitHub secrets to maintain security.

To deploy manually or to another environment, configure your AWS credentials in GitHub secrets or through your local environment, and push to the staging branch.

## Project Structure

The main components of the project structure are as follows:

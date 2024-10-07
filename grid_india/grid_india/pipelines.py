# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import pdfplumber
import pandas as pd
import numpy as np
import re
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials


SERVICE_ACCOUNT_FILE = './pruebascraping-aa36e3162617.json'
GOOGLE_DRIVE_FOLDER_PDF_ID = '1E5BIkwG7thVKwkp9Y8Uu8pIvDlZupB5V'
GOOGLE_DRIVE_FOLDER_CSV_ID = '1aLuf8TYB5Oym3zW86w1lcEP4T0J0L2_H'

def authenticate_drive():
    gauth = GoogleAuth()
    scope = ['https://www.googleapis.com/auth/drive']
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    return GoogleDrive(gauth)


drive = authenticate_drive()

column_mapping = {
    "regionregion": "region",
    "region": "region",
    "states": "state",
    "maxdemandmetduringthedaymw": "max_demand_met_day_mw",
    "shortageduringmaximumdemandmw": "shortage_during_max_demand_mw",
    "energymetmu": "energy_met_mu",
    "drawalschedulemu": "drawal_schedule_mu",
    "odudmu": "od_ud_mu",
    "maxodmw": "max_od_mw",
    "peakhourshortagemw": "peak_hour_shortage_mw",
    "energyshortagemu": "energy_shortage_mu"
}

class SavePdfPipeline:
    def process_item(self, item, spider):
        pdf_url = item['pdf_url']
        file_name = pdf_url.split('/')[-1]
        
        temp_path = os.path.join("./tmp", file_name)
        with open(temp_path, 'wb') as f:
            f.write(item['pdf_content'])
            f.close()

        gfile = drive.CreateFile({'parents': [{'id': GOOGLE_DRIVE_FOLDER_PDF_ID}], 'title': file_name})
        gfile.SetContentFile(temp_path)
        gfile.Upload()


        item['file_path'] = temp_path
        return item

class ProcessPdfPipeline:
    dataframes = []

    def process_item(self, item, spider):
        file_path = item['file_path']
        print(f"Procesando: {file_path}")

        processed_table = self.extract_and_process_table(file_path)
        if not processed_table.empty:
            processed_table['year'] = item['year']
            self.dataframes.append(processed_table)
            csv_file_name = file_path.replace('.pdf', '_table.csv')
            csv_temp_path = os.path.join("./tmp", csv_file_name)
            
            processed_table.to_csv(csv_temp_path, index=False)
            gfile = drive.CreateFile({'parents': [{'id': GOOGLE_DRIVE_FOLDER_CSV_ID}], 'title': csv_file_name})
            gfile.SetContentFile(csv_temp_path)
            gfile.Upload()
            print(f"Tabla CSV subida a Google Drive: {csv_file_name}")

            item['table_csv'] = csv_file_name
            item['data'] = processed_table

        return item

    def extract_and_process_table(self, pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if "power supply position in states" in text.lower():
                    for table in page.extract_tables():
                        df = pd.DataFrame(table).replace({r'\n': ' ', r'\r': ' '}, regex=True)
                        df = self.process_table(df)
                        
                        if not df.empty:
                            df = self.standardize_column_names(df)
                            df = df[~df.iloc[:, 1:].isna().all(axis=1)].reset_index(drop=True)
                            df.iloc[:, 0] = df.iloc[:, 0].fillna(method='ffill')
                            df = df.replace({'-': np.nan})
                            return df
        return pd.DataFrame()

    def process_table(self, df):
        if len(df.columns)>2:
            data = df.iloc[:, 2].astype(str).str.lower().str.replace(' ', '')
            index = data[data.str.contains('max.demandmetduringtheday')].index
            if not index.empty:
                df.columns = df.iloc[index[0]]
                df = df.iloc[index[0] + 1:].reset_index(drop=True)
                return df
        return pd.DataFrame()

    def clean_column_name(self, col):
        col_clean = re.sub(r"[ .()/+-]", "", str(col)).lower()
        return column_mapping.get(col_clean, col)

    def standardize_column_names(self, df):
        df.columns = [self.clean_column_name(col) for col in df.columns]
        return df
    
    def close_spider(self, spider):
        if self.dataframes:
            compiled_df = pd.concat(self.dataframes, ignore_index=True)
            compiled_csv_path = os.path.join("./tmp", 'compiled_tables.csv')
            compiled_df.to_csv(compiled_csv_path, index=False)
            gfile = drive.CreateFile({'parents': [{'id': GOOGLE_DRIVE_FOLDER_CSV_ID}], 'title': 'compiled_tables.csv'})
            gfile.SetContentFile(compiled_csv_path)
            gfile.Upload()
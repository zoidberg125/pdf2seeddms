#!/usr/local/bin/python3
import logging
import requests
import argparse
import os
import sys
import json
import swagger_client
import seeddms
from pathlib import Path
from swagger_client.api import Pdf2seeddmsApi
from rfc5424logging import Rfc5424SysLogHandler


def upload2seeddms(file, seeddmsURL,seedUser, seedPWD):
    logging.info("uploading file to SeedDMS")
    config = seeddms.Config(baseurl=seeddmsURL,
                            username=seedUser,
                            password=seedPWD
                            )
    sdms = seeddms.SeedDMS(baseurl = config.baseurl,
                       username = config.username,
                       password = config.password,
                       targetfolder = config.targetfolder)
    sdms.do_login()
    sdms.upload_document(folder_id=6, documentpath=file, name=Path(file).stem)


def pdf2seeddms(directory, orcapiurl,logger, seeddmsURL,seedUser, seedPWD):
    logging.info("iterating over files and uploading them to SeedDMS")
    config = swagger_client.Configuration()
    config.host = orcapiurl
    config.logger = logger
    api_client = swagger_client.ApiClient(configuration=config)
    api_instance = Pdf2seeddmsApi(api_client)
    dirName = os.path.join(directory,"back")
    if not os.path.exists(dirName):
        os.mkdir(dirName)
        logging.info("Directory " + dirName +  " Created ")
    else:
        logging.info("Directory " + dirName + "already exist")

    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            logging.info("Uploading " + filename + " to OCR API")
            results = api_instance.post_pdf2seeddmsul(os.path.join(directory,filename),_preload_content=False)
            logging.info("Before writing file "+ filename + " back move old one into back directory")
            os.system("mv "+ os.path.join(directory,filename) +" "+os.path.abspath(dirName))
            with open(os.path.join(directory,filename), "wb+") as f:
                f.write(results.data)
            upload2seeddms(file=os.path.join(directory,filename),seeddmsURL=seeddmsURL,seedUser=seedUser,seedPWD=seedPWD)
            os.remove(os.path.join(directory,filename))
        else:
            continue

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    syslog = Rfc5424SysLogHandler(address=('192.168.178.35', 514), appname="pdf2seeddms")
    syslog.setLevel(level=logging.INFO)
    root_logger = logging.getLogger()
    root_logger.addHandler(syslog)
    return root_logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OCR all PDFs in Folder and import them into SeedDMS')
    required_list_columns = parser.add_argument_group('Required for the script')
    required_list_columns.add_argument('-d', '--input-directory',dest='directory',help='input directory', required=True)
    required_list_columns.add_argument('-u', '--ocr-api-url',dest='orcapiurl',help='OCR API URL', required=True)
    required_list_columns.add_argument('-s', '--seeddms-api-url',dest='seeddmsurl',help='SeedDMS API URL', required=True)
    required_list_columns.add_argument('-n', '--seeddms-user',dest='seeddmsuser',help='SeedDMS User', required=True)
    required_list_columns.add_argument('-p', '--seeddms-pwd',dest='seeddmspwd',help='SeedDMS Pwd', required=True)
    args = parser.parse_args()
    root_logger = setup_logging()
    try:
        pdf2seeddms(args.directory, args.orcapiurl,root_logger,args.seeddmsurl,args.seeddmsuser,args.seeddmspwd)
    except Exception as e:
        root_logger.exception("File conversion failed")
        sys.exit(1)

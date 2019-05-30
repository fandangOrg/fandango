'''
Created on Jan 21, 2019

@author: daniele
'''
import time
from threading import Thread
from fake_news_detection.config.AppConfig import url_kafka, port_kafka,\
    n_consumer, topic_input_kafka, topic_output_kafka
from fake_news_detection.business.jobs import run_job
from fake_news_detection.apps.Task import Task_Analyzer

#import schedule


def daemon_run():
    threads = []
    #===========================================================================
    # In this case 'urls' is a list of urls to be crawled. 
    #     We start one thread per url present.
    #===========================================================================
    print("coda: ",url_kafka, port_kafka )
    print("RUN ANALYZER")
    process = Thread(target=run_job, kwargs={"n_job":n_consumer,"input_queue":topic_input_kafka,"output_queue":topic_output_kafka,"task": Task_Analyzer})
    process.start()
    threads.append(process)
 
    
if __name__ == '__main__':

    daemon_run()
    #===========================================================================
    # print("RUN SCHEDULER")
    # process = Thread(target=schedule_task)
    # process.start()
    # threads.append(process)
    #===========================================================================
    

#===============================================================================
# def schedule_task():
# 
#     # task che esegue la pulizia/auto-revisione degli articoli salvati
#     # schedule.every().day.at("00:01").do(run_cleaner_job)
# 
#     # task che manda per mail il report del crawling
#     schedule.every().day.at("08:05").do(task_daily_report)
#     #schedule.every(10).minutes.do(task_daily_report)
#     # task che esegue l'ingestion dei domani per il crawling
#     #schedule.every(1).minutes.do(ingestion_domains)
#     schedule.every(2).hours.do(ingestion_domains)
#     while True:
# 
#         schedule.run_pending()
#         time.sleep(1)
#===============================================================================

#===============================================================================
# 
# def scheduled_deamons_run():
# 
#     threads = []
#     print("RUN SCHEDULER")
#     process = Thread(target=schedule_task)
#     process.start()
#     threads.append(process)
#===============================================================================
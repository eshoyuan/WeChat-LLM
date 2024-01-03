import json
import csv
import os
from datetime import datetime

def read_csv(file_path):
    data = []
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)
        col2idx = {col: idx for idx, col in enumerate(header)}
        for row in reader:
            if row[col2idx['StrContent']] == '' or "md5" in row[col2idx['StrContent']]:
                # 跳过空消息和图片消息
                continue
            if row[col2idx['Type']] == '10000':
                # 跳过系统消息
                continue
            data.append([row[col2idx['IsSender']],
                        row[col2idx['StrTime']], row[col2idx['StrContent']]])
    return data

def is_within_one_hour(time1, time2):
    datetime_format = "%Y-%m-%d %H:%M:%S"
    time1 = datetime.strptime(time1, datetime_format)
    time2 = datetime.strptime(time2, datetime_format)
    return (time2 - time1).seconds <= 3600

def process_data(data):
    record = []
    last_sender = ""
    for i in range(len(data)):
        sender = "朋友" if data[i][0] == '0' else "我"
        message = data[i][2]

        if sender == last_sender and i > 0 and is_within_one_hour(data[i - 1][1], data[i][1]):
            # 合并一小时内的消息, 对应一个句子分多次发出的情况
            record[-1] = record[-1] + ", " + message
        else:
            record.append(f"{sender}: {message}")
        last_sender = sender
    return record

def main():
    all_data = []
    for file_name in os.listdir('./data/raw_data'):
        if file_name.endswith('.csv'):
            file_path = os.path.join('./data/raw_data', file_name)
            all_data.extend(read_csv(file_path))

    processed_data = process_data(all_data)

    with open('./data/chat.txt', mode='w') as file:
        file.write("\n".join(processed_data))

if __name__ == "__main__":
    main()

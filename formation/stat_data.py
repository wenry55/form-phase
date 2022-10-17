from random import randint
from tkinter import W
from matplotlib import is_url
import numpy as np
import pandas as pd
from threading import Thread
from queue import Queue
import time

# stage states
IN_CHARGE = 1
NOOP = 2

df_all = pd.read_parquet('all.gzip')
keys = [key for key in df_all.groupby('stage').groups.keys()]
stage_data = [df_all.query('stage == @stage') for stage in keys]


class Dataset():
    pass


class DataLoader():

    def get(self, lane_id, stage_id):
        stage = int(lane_id * 48) * int(stage_id) % 4
        if lane_id == '6' and stage_id == '48':
            print('faulty loaded at 6, 48')
            return pd.read_parquet('./faulty.gzip')
        else:
            return stage_data[stage]

    def get_same_channels(self, channel_no):
        df_channels = df_all.query('channel == @channel_no')
        return df_channels


dataloader = DataLoader()


class Channel(object):
    voltage = 0
    current = 0
    state = []

    def __init__(self, channel_id, period_from=1) -> None:
        self.channel_id = channel_id
        self.vol = 0
        self.curr = 0
        self.pv = 0
        self.elapsed = '0000:00:00'
        self.q_val = 0

    def put(self):
        pass

    def get_vol(self):
        pass

    def get_expected(self):
        pass


class Stage(object):

    num_thermal = 12
    num_channels = 56
    num_lanes = 6

    def __init__(self, dataloader, lane_id, stage_id) -> None:
        self.lane_id = lane_id
        self.stage_id = stage_id
        self.state = NOOP
        self.channels = [Channel(i) for i in range(1, 57)]  # 1~56
        self.temperatures = [np.nan for i in range(13)]  # 1~12

        self.dataloader = dataloader
        self.queue = Queue()
        self.data = dataloader.get(lane_id, stage_id)
        self.is_running = False
        self.current_step = 0
        

    def get_state(self):
        return self.state

    def task(self):
        while True:
            data = self.queue.get()
            print(
                f'Reporting {self.lane_id},{self.stage_id} : {self.state}, {data}'
            )

    def put(self, data):
        self.queue.put(data)

    def load(self, lane_id, stage_id):
        pass

    def progressor(self):
        while self.is_running:
            time.sleep(1)
            self.current_step += 10
            # print('current step : ', self.current_step, self.lane_id, self.stage_id)


    def start(self, from_step):
        if self.is_running:
            self.is_running = False
            return

        self.is_running = True
        self.current_step = from_step
        progress = Thread(target=self.progressor)
        progress.start()



stages = {}

for lane_id in range(1, 7):
    stages[str(lane_id)] = {}
    for stage_id in range(1, 49):
        s = Stage(dataloader, str(lane_id), str(stage_id))
        stages[str(lane_id)][str(stage_id)] = s
        # t = Thread(target=s.task)
        # t.start()
        
        s.start(randint(1, 20000))


print('Stages are loaded')
#for lane_id in stages.keys():
#    for stage_id in stages[lane_id].keys():
#        s = stages[lane_id][stage_id]
#        s.put(f'hello {lane_id}, {stage_id}')

df_tempers = pd.read_parquet('all_temperature.gzip')
# print(df_tempers)
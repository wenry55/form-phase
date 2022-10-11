from multiprocessing import Event
import uuid
import threading
import click
import sys, os
import cmd
import pandas as pd
import numpy as np
from queue import Queue


@click.command()
@click.option("--count", default=1, help="Number of greetings.")
@click.option("--name", prompt="Your name", help="The person to greet.")
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for _ in range(count):
        click.echo(f"Hello, {name}!")


DATA_DIR = './data/'

q = Queue()


# rps : records for second
def feed_task(q, df, rps=1, period_from=1):
    count = 0

    while q.empty():
        #print(data)
        count += 1
        targets = df.query(
            'series >= (@count * @rps) and series < ((@count + 1)*@rps)')
        print(targets)
        Event().wait(1)
    q.get()


class Feeder(cmd.Cmd):
    intro = 'Data feeder shell.'
    prompt = 'feeder > '
    file_list = None
    cache_list = {}

    def emptyline(self) -> bool:
        return False

    def do_exit(self, arg):
        return True

    def do_ls(self, arg):
        if self.file_list is None:
            self.file_list = os.listdir('./data')

        for k, file in enumerate(self.file_list):
            print(f'[{k}]', file)

    def do_send(self, arg):
        'send selected file as data, n(batch) records per second for a stage.\n\n' \
        'ex) s 0 3 will send first file in ls and send 3 time steps for a second evenly (prox. 0.33)'

        if self.file_list is None:
            self.file_list = os.listdir('./data')

        args = arg.split(' ')
        # print(len(args))
        # print(arg, len(arg))
        # print(args)
        if len(arg) == 0:
            print('Specify file index from ls')
            self.do_ls(None)
            return False

        file_name = self.file_list[int(args[0])]

        target_df = None
        if file_name in self.cache_list.keys():
            # use cached
            print("Using cached.")
            target_df = self.cache_list[file_name]
            pass
        else:
            df = pd.read_csv(DATA_DIR + file_name, encoding='euc-kr')
            channs = []
            for i in range(1, 57):
                df_sc = df[[
                    '시간', f'ch{i} 전압', f'ch{i} 전류', f'ch{i} 용량', f'ch{i} PV'
                ]].copy()
                df_sc = df_sc.rename(
                    columns={
                        '시간': 'ds',
                        f'ch{i} 전압': 'vol',
                        f'ch{i} 전류': 'curr',
                        f'ch{i} 용량': 'q_val',
                        f'ch{i} PV': 'pv'
                    })
                df_sc['stage'] = file_name
                df_sc['ch'] = str(i)
                df_sc['series'] = np.arange(1, len(df_sc) + 1)

                channs.append(df_sc)

            target_df = pd.concat(channs)
            self.cache_list[file_name] = target_df

        print(len(target_df))

        t = threading.Thread(target=feed_task, args=(q, target_df, 5, 0))
        t.start()

        input("Press Enter to stop...\n")
        q.put("stop")


if __name__ == '__main__':
    Feeder().cmdloop()
import pandas as pd

def nodes_throughput(df):

    if df.empty:
        return 0
    groups = df.groupby('id')['timestamp'].aggregate(lambda x : x.count()/float(x.max()-x.min()))
    return groups.mean()

def model():
    return pd.DataFrame(columns=['timestamp', 'response_time', 'id', 'hostname', 'node'])


def insert_data(response):
    new_df = pd.DataFrame(response['request_data'], columns=['timestamp', 'response_time', 'id'])
    new_df['hostname'] = pd.Series([response['hostname']] * len(new_df))
    new_df['node'] = pd.Series([response['node']] * len(new_df))
    return new_df
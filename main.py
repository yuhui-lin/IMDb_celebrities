from pathlib import Path
import pandas as pd
import itertools
import networkx as nx
import community
import matplotlib.pyplot as plt

from help import logging, set_logging, write_json
import get_cele

# the top number of celebrities to be analyzed (500 max)
NUM_CELE = 200
DATA_P = Path('data/')
OUTPUT_P = Path('output/')
# CELE_JSON_P = DATA_P / 'cele_top.json'
GRAPH_JSON_P = OUTPUT_P / f'graph_{NUM_CELE}.json'
NAME_BASICS_P = DATA_P / 'name.basics.tsv'
TITLE_CREW_P = DATA_P / 'title.crew.tsv'
TITLE_PRIN_P = DATA_P / 'title.principals.tsv'
TITLE_BASIC_P = DATA_P / 'title.basics.tsv'

def main():
    set_logging(stream=True)
    graph = nx.Graph()
    set_nodes(graph)
    set_edges(graph)
    
    logging.info('run Louvain method...')
    partition = community.best_partition(graph)
    p_tvEps = community.best_partition(graph, weight='w_tvEps')
    p_movie = community.best_partition(graph, weight='w_movie')
    # add partition to nodes
    for node in graph.nodes():
        graph.node[node]['partition'] = partition[node]
        graph.node[node]['p_tvEps'] = p_tvEps[node]
        graph.node[node]['p_movie'] = p_movie[node]
        graph.node[node]['degree'] = graph.degree(node)
        graph.node[node]['degree_weight'] = graph.degree(node, weight='weight')
        graph.node[node]['degree_tvEps'] = graph.degree(node, weight='w_tvEps')
        graph.node[node]['degree_movie'] = graph.degree(node, weight='w_movie')

    nodes = [{**i[1], **{'id': i[0]}} for i in graph.nodes(data=True)]
    links = [{**i[2], **{'source':i[0], 'target':i[1]}}
                for i in graph.edges(data=True)]
    write_json(GRAPH_JSON_P, {'nodes':nodes, 'links':links})

    draw_louvain(graph, partition)
    logging.info("\nDone")
    
def read_csv(p):
    logging.info(f'start reading csv: {p}')
    ret_df = pd.read_csv(p, sep='\t')
    print_df_info(ret_df, str(p))
    return ret_df

def print_df_info(df, name):
    logging.info(f'{name} shape: {df.shape}')
    logging.info(f'{name} head:\n{df.head()}')

def set_nodes(graph):
    with get_cele.TOP_CELE_P.open() as f:
        cele_df = pd.read_json(f, orient='records')[:NUM_CELE]
    print_df_info(cele_df, 'cele_df')

    name_df = read_csv(NAME_BASICS_P)

    nodes_df = pd.merge(cele_df, name_df, on='nconst')
    print_df_info(nodes_df, 'nodes')

    def add_node(row):
        # logging.info('row: ', row)
        graph.add_node(row['nconst'], bio=row['bio'],
            name=row['primaryName'], birthYear=row['birthYear'],
            primaryProfession=row['primaryProfession'])
    nodes_df.apply(add_node, axis=1)
    return graph

def get_cast_df():
    crew_df = read_csv(TITLE_CREW_P)
    prin_df = read_csv(TITLE_PRIN_P)
    # cast_df = pd.merge(crew_df, prin_df, on='tconst')
    # cast_df = crew_df.merge(prin_df, on='tconst', sort=False)
    cast_df = pd.merge(crew_df, prin_df, on='tconst', sort=False)
    # do not handle \N because it will be remove later
    cast_df['cast'] = cast_df['directors'] + ',' + cast_df['writers'] + \
        ',' + cast_df['principalCast']
    # OR use df.drop()
    # cast_df.drop(['directors', 'writers', 'principalCast'], \
    # axis=1, inplace=True)
    cast_df = cast_df.loc[:, ['tconst', 'cast']]

    title_df = read_csv(TITLE_BASIC_P)
    logging.info(f'titleType: \n{title_df["titleType"].value_counts()}')
    cast_df = pd.merge(cast_df, title_df, on='tconst', sort=False)

    return cast_df.loc[:, ['tconst', 'cast', 'titleType', 'primaryTitle']]

def set_edges(graph):
    # col: tconst, cast(str of nconst seperated by comma)
    cast_df = get_cast_df()
    print_df_info(cast_df, 'cast_df')

    # row is namedtuple
    for row in cast_df.itertuples():
        w_tvEps, w_movie = 0, 0
        if row.titleType in ('tvEpisode'):
            w_tvEps = 1
        # elif row.titleType in ('short', 'movie', 'video', 'tvMovie'):
        elif row.titleType in ('movie', 'tvMovie'):
            w_movie = 1

        cast = row.cast.split(',')
        # remove duplicate
        top_cast = {c for c in cast if c in graph.nodes()}
        for edge in itertools.combinations(top_cast, 2):
            logging.info(f'new edge: {edge}')
            if graph.has_edge(edge[0], edge[1]):
                graph[edge[0]][edge[1]]['weight'] += 1
                graph[edge[0]][edge[1]]['tconsts'].append(row.tconst)
                graph[edge[0]][edge[1]]['w_tvEps'] += w_tvEps
                graph[edge[0]][edge[1]]['w_movie'] += w_movie
            else:
                graph.add_edge(edge[0], edge[1], weight=1, 
                    tconsts=[row.tconst], w_tvEps=w_tvEps, w_movie=w_movie)
    return graph

    # title_name_df = cast_df.set_index('tconst') \
    #     .loc['cast'] \
    #     .apply(lambda x: pd.Series(x.split(','))) \
    #     .stack() \
    #     .reset_index()
    #     # .rename(columns={}) \
    # title_name_df.columns = ['tconst', 'cast_num', 'cast']
    # # col: tconst, nconst(includes \N)
    # title_name_df.drop('cast_num', axis=1, inplace=True)
    # # col: tconst, nconst(top_nconst)
    # title_name_df = title_name_df[title_name_df['cast'].isin(top_nconst)]

def draw_louvain(G, partition):
    #drawing
    size = float(len(set(partition.values())))
    pos = nx.spring_layout(G)
    count = 0.
    for com in set(partition.values()) :
        count = count + 1.
        list_nodes = [nodes for nodes in partition.keys()
                                    if partition[nodes] == com]
        nx.draw_networkx_nodes(G, pos, list_nodes, node_size = 20,
                                    node_color = str(count / size))

    nx.draw_networkx_edges(G, pos, alpha=0.5)
    plt.show()

if __name__ == '__main__':
    main()
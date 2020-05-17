import sys
import pandas as pd
import random
import math

original_bidders = pd.read_csv('bidder_dataset.csv')
original_budget = original_bidders[['Advertiser', 'Budget']]
original_budget = original_budget.dropna()
original_budget_map = original_budget.set_index('Advertiser').to_dict()['Budget']


def read_data():
    queries = pd.read_fwf('queries.txt', header=None)
    bidders = pd.read_csv('bidder_dataset.csv')
    budgets = bidders[['Advertiser', 'Budget']]

    # budget manipulation, not required after creating budget map
    budgets = budgets.dropna()
    budget_map = budgets.set_index('Advertiser').to_dict()['Budget']
    bidders = bidders.drop(['Budget'], axis=1)

    bidder_query_map = {}
    for i in range(0, len(bidders)):
        keyword = bidders.iloc[i, 1]
        advertiser = bidders.iloc[i, 0]
        bid_val = bidders.iloc[i, 2]
        if keyword not in bidder_query_map:
            bidder_query_map[keyword] = {}
        bidder_query_map[keyword][advertiser] = bid_val
    return queries, bidder_query_map, budget_map


def compute(queries, bidder_query_map, budget_map, find_bidder):
    revenue = 0.0
    for q in range(0, len(queries)):
        query = queries.iloc[q, 0]
        bidder = find_bidder(query, bidder_query_map, budget_map)
        if bidder == -1:
            continue
        bid_value = bidder_query_map[query][bidder]
        revenue += bid_value
        budget_map[bidder] -= bid_value
    return revenue


def greedy(query, bidder_query_map, budget_map):
    temp = bidder_query_map[query]
    keys = temp.keys()
    for key in list(keys):
        if budget_map[key] < temp[key]:
            temp.pop(key)
    if not temp:
        return -1
    max_bidder = max(temp, key=temp.get)
    return max_bidder


def balance(query, bidder_query_map, budget_map):
    temp = bidder_query_map[query]
    temp_budget_map = {}

    for key in temp.keys():
        temp_budget_map[key] = budget_map[key]

    max_unspent_bidder = max(temp_budget_map, key=temp_budget_map.get)

    if temp_budget_map[max_unspent_bidder] <= 0:
        return -1
    return max_unspent_bidder


def msvv(query, bidder_query_map, budget_map):
    temp = bidder_query_map[query]
    temp_budget_map = {}
    keys = temp.keys()
    for key in list(keys):
        if budget_map[key] < temp[key]:
            temp.pop(key)
    if not temp:
        return -1

    for key in temp.keys():
        xu = (original_budget_map[key] - budget_map[key])/original_budget_map[key]
        psi_xu = 1 - math.exp(xu-1)
        temp_budget_map[key] = (temp[key] * psi_xu)

    max_msvv_bidder = max(temp_budget_map, key=temp_budget_map.get)
    return max_msvv_bidder


def competitive_revenue(algorithm):
    queries, bidder_query_map, budget_map = read_data()
    optimal_matching = sum(budget_map.values())
    total_revenue = 0.0
    for i in range(0, 100):
        random.seed(0)
        queries, bidder_query_map, budget_map = read_data()
        total_revenue += compute(queries, bidder_query_map, budget_map, algorithm)
    mean_revenue = total_revenue/100
    print(mean_revenue)
    comp_ratio = mean_revenue/optimal_matching
    print(comp_ratio)


def main():
    if sys.argv[1] == 'greedy':
        competitive_revenue(greedy)
    if sys.argv[1] == 'balance':
        competitive_revenue(balance)
    if sys.argv[1] == 'msvv':
        competitive_revenue(msvv)


if __name__ == "__main__":
    main()

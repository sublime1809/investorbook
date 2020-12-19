import copy
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

from models import Investor, Investment


class ShortestPathInvestor:
    def __init__(self, source_investor: Investor, destination_investors: set):
        self._destination_investors = destination_investors
        self._source = source_investor
        self._all_investors = self._destination_investors.union({self._source})

        self._graph = self._init_mst()
        print(f'Starting graph: {self._graph}')

    def get_connection_degree(self, dest: Investor):
        return self._graph[self._source.id][dest.id]

    def run_expanding_dijkstra(self):
        visited_ids = list()

        self._run_dijkstra(visited_ids)
        next_investors = copy.deepcopy(self._destination_investors)
        while any([self._graph[self._source.id][dest.id] == sys.maxsize
                   for dest in self._destination_investors]):
            print(f'Not finished -- getting next level...')
            next_investors = self._add_next_level(next_investors)
            print(f'     {sorted(list(next_investors), key=lambda i: i.id)}')
            if not next_investors:
                break
            self._run_dijkstra(visited_ids)
        print('Filled all investors: ')
        for d in self._destination_investors:
            print(f'{self._source.id} -> {d.id} ===> '
                  f'{self._graph[self._source.id][d.id]}')

    def _add_next_level(self, investors: set):
        next_level = set()
        for i in investors:
            new_investors = self._first_degree_connections(i)
            next_level.update(new_investors)
            for j in new_investors:
                self._add_investor(j, i)
            print(f'     {sorted(list(next_level), key=lambda i: i.id)} - {sorted(list(self._all_investors), key=lambda i: i.id)}')
            self._all_investors.update(new_investors)
            print(f'Updated graph: {self._graph[self._source.id]}')
        next_level = next_level.difference(self._all_investors)
        print(f'     equals {sorted(list(next_level), key=lambda i: i.id)}')
        return next_level

    @staticmethod
    def _first_degree_connections(investor: Investor):
        # This really should be reused in a more generic way,
        #   but in the interest of time, I'm just running with the duplication.
        investments = db.session.query(Investment).filter_by(investor_id=investor.id)
        companies = [i.company for i in investments]

        first_connections = set()
        for company in companies:
            investors = company.investors
            first_connections.update(investors)

        return first_connections

    def _run_dijkstra(self, visited_ids: list):
        for i in self._all_investors:
            u = self._min_distance(i.id, visited_ids)
            visited_ids.append(u)

            for j in self._all_investors:
                if self._graph[i.id][j.id] > 0 and j.id not in visited_ids:
                    new_distance = self._graph[self._source.id][i.id] + self._graph[
                        i.id][j.id]
                    if self._graph[self._source.id][j.id] > new_distance:
                        self._graph[self._source.id][j.id] = new_distance
                        self._graph[j.id][self._source.id] = new_distance

    def _min_distance(self, src_id, visited_ids):

        min = sys.maxsize
        min_index = None
        dist = self._graph[src_id]

        for i in self._all_investors:
            if dist[i.id] < min and i.id not in visited_ids:
                min = dist[i.id]
                min_index = i.id

        return min_index

    def _init_mst(self):
        graph = {i.id: {
            investor.id: 0 if investor.id == i.id else sys.maxsize
            for investor in self._all_investors} for i in self._all_investors}
        return graph

    def _add_investor(self, investor: Investor, src_investor: Investor):
        if investor.id not in self._graph:
            self._graph.update({
                investor.id: {
                    i.id: 0 if investor.id == i.id else sys.maxsize
                    for i in self._all_investors}})
            for c in self._all_investors:
                self._graph[c.id].update({investor.id: sys.maxsize})

        # Add the one step that caused the addition of the new investor
        self._graph[investor.id][src_investor.id] = 1
        self._graph[src_investor.id][investor.id] = 1

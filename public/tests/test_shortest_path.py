import unittest
from unittest import mock

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from models import Investor, Investment, Company, db
from shortest_path import ShortestPathInvestor


class TestShortestPathInvestor(unittest.TestCase):
    Base = declarative_base()
    engine = create_engine('sqlite:///:memory:')

    def setUp(self):
        Session = sessionmaker()
        Session.configure(bind=self.engine)
        session = Session()

        self.investor = Investor(1, 'Number 1')
        self.first_connection = Investor(2, 'Number 2')

        company = Company(1, 'Best Company')

        investment = Investment(1, self.investor, company, amount=1200)
        investment_first = Investment(2, self.first_connection, company, amount=200)

        session.add(self.investor)
        session.add(self.first_connection)
        session.add(company)
        session.add(investment)
        session.add(investment_first)
        self.Base.metadata.create_all(self.engine)

        self.shortest_path = ShortestPathInvestor(self.investor, {self.first_connection})

    def test_first_connection(self):
        self.shortest_path.run_expanding_dijkstra()
        print(self.shortest_path._graph)
        actual_degree = self.shortest_path.get_connection_degree(self.first_connection)

        self.assertEqual(actual_degree, 1)

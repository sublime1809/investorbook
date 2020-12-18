from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from models import Company, Investor, Investment
from shortest_path import InvestorGraph


@app.route('/')
def hello():
    return 'HELLO!'


def _first_degree_connections(investor_id):
    investor = Investor.query.filter_by(id=investor_id).first()
    if not investor:
        return list()
    companies = investor.companies

    first_connections = set()
    for company in companies:
        investors = company.investors
        first_connections = first_connections.union(investors)

    return first_connections


@app.route('/investors/<investor_id>/connections')
def connections(investor_id):
    first_connections = _first_degree_connections(investor_id)

    return jsonify([investor.jsonify() for investor in first_connections])


@app.route('/investors/<investor_id>/mutual/<other_investor_id>')
def mutual(investor_id, other_investor_id):
    first_connections = _first_degree_connections(investor_id)
    other_first_connections = _first_degree_connections(other_investor_id)

    mutual_connections = first_connections.intersection(other_first_connections)

    return jsonify([investor.jsonify() for investor in mutual_connections])


def _map_company_depth(investor: Investor, evaluated_companies: dict, connection=1):
    companies = investor.companies
    new_companies = set()
    for company in companies:
        if company.id not in evaluated_companies.keys():
            print(f'Adding {company} to {new_companies}')
            new_companies.add(company)
            evaluated_companies.update({company.id: connection})
        else:
            # get the smallest connection -- this shouldn't happen since we only add
            # after
            if evaluated_companies[company.id] > connection:
                evaluated_companies[company.id] = connection
    for company in new_companies:
        investors = company.investors
        for investor in investors:
            _map_company_depth(investor, evaluated_companies, connection+1)


@app.route('/investors/<investor_id>/search')
def search(investor_id):
    search_string = request.args.get('q')
    print(f'Search Term: {search_string}')
    investor = Investor.query.filter_by(id=investor_id).first()

    search_results = dict()
    investors = Investor.query.filter(Investor.name.like(f'%{search_string}%')).all()
    print(f'Found {len(investors)} investors matching search')
    graph = InvestorGraph(investor, set(investors))
    graph.run_expanding_dijkstra()
    for investor in investors:
        search_results.update({investor.id: graph.get_connection_degree(investor)})
    return jsonify(search_results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

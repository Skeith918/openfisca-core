#! /usr/bin/env python
# -*- coding: utf-8 -*-


# OpenFisca -- A versatile microsimulation software
# By: OpenFisca Team <contact@openfisca.fr>
#
# Copyright (C) 2011, 2012, 2013, 2014, 2015 OpenFisca Team
# https://github.com/openfisca
#
# This file is part of OpenFisca.
#
# OpenFisca is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# OpenFisca is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Convert a scenario or simulation JSON containing a test case to the same JSON with input variables."""


import argparse
import copy
import importlib
import json
import logging
import sys

from biryani.baseconv import check


args = None


def json_with_test_case_to_input_variables(scenario_or_simulation_json):
    country_package = importlib.import_module(args.country_package_name)
    TaxBenefitSystem = country_package.init_country()
    tax_benefit_system = TaxBenefitSystem()
    new_scenario_or_simulation_json = copy.deepcopy(scenario_or_simulation_json)
    new_scenarios_json = new_scenario_or_simulation_json['scenarios'] \
        if 'scenarios' in new_scenario_or_simulation_json \
        else [new_scenario_or_simulation_json]
    assert all('test_case' in scenario_json for scenario_json in new_scenarios_json), \
        'All the scenarios must have a test case.'
    for new_scenario_json in new_scenarios_json:
        scenario = check(tax_benefit_system.Scenario.make_json_to_instance(
            repair = True,
            tax_benefit_system = tax_benefit_system,
            ))(new_scenario_json)
        scenario.suggest()
        simulation = scenario.new_simulation(use_set_input_hooks = False)
        input_variables_json = simulation.to_input_variables_json()
        del new_scenario_json['test_case']
        new_scenario_json['input_variables'] = input_variables_json
    return new_scenario_or_simulation_json


def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('country_package_name', help = "country package name (ex: openfisca_france)")
    parser.add_argument('-i', '--input-file', type = argparse.FileType('r'), default = '-', help = 'JSON scenario')
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    global args
    args = parser.parse_args()
    logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING, stream = sys.stdout)
    scenario_or_simulation_str = args.input_file.read()
    scenario_or_simulation_json = json.loads(scenario_or_simulation_str)
    new_scenario_or_simulation_json = json_with_test_case_to_input_variables(scenario_or_simulation_json)
    print json.dumps(new_scenario_or_simulation_json, indent = 2, sort_keys = True).encode('utf-8')


if __name__ == "__main__":
    sys.exit(main())
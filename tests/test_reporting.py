"""Tests for ixmp.reporting."""

import ixmp
import ixmp.reporting
from ixmp.reporting import Key, Reporter
import pandas as pd
import pytest
import xarray as xr

from ixmp.testing import dantzig_transport

test_args = ('Douglas Adams', 'Hitchhiker')

TS_DF = {'year': [2010, 2020], 'value': [23.7, 23.8]}
TS_DF = pd.DataFrame.from_dict(TS_DF)
TS_DF['region'] = 'World'
TS_DF['variable'] = 'Testing'
TS_DF['unit'] = '???'


@pytest.fixture
def scenario(test_mp):
    # from test_feature_timeseries.test_new_timeseries_as_year_value
    scen = ixmp.Scenario(test_mp, *test_args, version='new', annotation='foo')
    scen.add_timeseries(TS_DF)
    scen.commit('importing a testing timeseries')
    return scen


def test_reporting_key():
    k1 = Key('foo', ['a', 'b', 'c'])

    # Representation
    assert repr(k1) == 'foo:a-b-c'

    # Key hashes the same as its string representation
    assert hash(k1) == hash('foo:a-b-c')

    # Key compares equal to its string representation
    assert k1 == 'foo:a-b-c'

    # Number of aggregates for a 3-dimensional quantity
    assert sum(1 for a in k1.aggregates()) == 7


def test_reporter(scenario):
    r = Reporter.from_scenario(scenario)

    r.finalize(scenario)

    # TODO add some assertions


def test_reporter_from_dantzig(test_mp, test_data_path):
    scen = dantzig_transport(test_mp, solve=test_data_path)

    # Reporter.from_scenario can handle the Dantzig problem
    rep = Reporter.from_scenario(scen)

    # Aggregates are available automatically (d is defined over i and j)
    d_i = rep.get('d:i')

    # Units pass through summation
    assert d_i.attrs['unit'] == 'km'

    # Disaggregation with explicit data
    # (cases of canned food 'p'acked in oil or water)
    shares = xr.DataArray([0.8, 0.2], coords=[['oil', 'water']], dims=['p'])
    rep.disaggregate('b:j', 'p', args=[shares])
    b_jp = rep.get('b:j-p')

    # Units pass through disaggregation
    assert b_jp.attrs['unit'] == 'cases'

    # Set elements are available
    assert rep.get('j') == ['new-york', 'chicago', 'topeka']

    # 'all' key retrieves all quantities
    names = set('a b d f demand demand-margin z x'.split())
    assert names == {da.name for da in rep.get('all')}


def test_reporter_read_config(test_mp, test_data_path):
    scen = dantzig_transport(test_mp)

    rep = Reporter.from_scenario(scen)
    with pytest.warns(UserWarning,
                      match=r"Unrecognized sections {'notarealsection'}"):
        rep.read_config(test_data_path / 'report-config-0.yaml')

    # Data from configured file is available
    assert rep.get('d_check').loc['seattle', 'chicago'] == 1.7


def test_reporter_disaggregate():
    r = Reporter()
    foo = Key('foo', ['a', 'b', 'c'])
    r.add(foo, '<foo data>')
    r.add('d_shares', '<share data>')

    # Disaggregation works
    r.disaggregate(foo, 'd', args=['d_shares'])

    assert 'foo:a-b-c-d' in r.graph
    assert r.graph['foo:a-b-c-d'] == (ixmp.reporting.disaggregate_shares,
                                      'foo:a-b-c', 'd_shares')

    # Invalid method
    with pytest.raises(ValueError):
        r.disaggregate(foo, 'd', method='baz')


def test_reporting_files(tmp_path):
    r = Reporter()

    # Path to a temporary file
    p = tmp_path / 'foo.txt'

    # File can be added to the Reporter before it is created, because the file
    # is not read until/unless required
    r.add_file(p)

    # Add some contents to the file
    p.write_text('Hello, world!')

    # The file's contents can be read through the Reporter
    assert r.get('file:foo.txt') == 'Hello, world!'

    # Write the report to file
    p2 = tmp_path / 'bar.txt'
    r.write('file:foo.txt', p2)

    # The Reporter produces the expected output file
    assert p2.read_text() == 'Hello, world!'

    # TODO test reading CSV data to xarray


def test_reporter_visualize(test_mp):
    scen = dantzig_transport(test_mp)
    r = Reporter.from_scenario(scen)

    r.visualize('visualize.png')

    # TODO compare to a specimen; place in a temporary directory

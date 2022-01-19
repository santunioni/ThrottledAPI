import random
from itertools import repeat

import pytest

from throttled.models import Hit, Rate


def test_rate_should_be_ordered_by_ratio():
    rate = Rate(100, 1)
    assert rate == Rate(1000, 10)
    assert rate > Rate(200, 3)
    assert rate < Rate(200, 1)


def test_rate_also_compares_with_number():
    rate = Rate(100, 1)
    assert rate == Rate(1000, 10).ratio
    assert rate > Rate(200, 3).ratio
    assert rate < Rate(200, 1).ratio


def test_rate_from_hits_mimics_their_ratio():
    hits = list(repeat(Hit(), 5))
    hits.extend(list(map(lambda hit: Hit(time=hit.time + 0.1), hits)))

    rate = Rate.from_hits(hits)
    assert rate.interval == 0.1
    assert rate.hits == 10
    assert rate.ratio == 100


def test_rate_attributes_from_empty_hits_are_zero():
    rate = Rate.from_hits([])
    assert rate.interval == 0
    assert rate.hits == 0
    assert rate.ratio == 0


def test_comparing_rate_with_unsupported_should_raise():
    rate = Rate(random.randint(0, 1000), random.random())
    obj = object()
    with pytest.raises(TypeError):
        assert rate == obj
    with pytest.raises(TypeError):
        assert rate != obj


def test_consecutive_hits_with_same_key_and_cost_should_be_equal():
    hit1 = Hit()
    hit2 = Hit()
    hit3 = Hit(time=hit1.time + 1)

    assert hit1 == hit2
    assert hit3 > hit1
    assert hit3 != hit2

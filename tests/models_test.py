from itertools import repeat

from throttled.models import Hit, Rate


def test_rate_ordering_by_ratio():
    r1 = Rate(100, 1)
    assert r1 == Rate(1000, 10)
    assert r1 > Rate(200, 3)
    assert r1 < Rate(200, 1)


def test_rate_ordering_against_number():
    r1 = Rate(100, 1)
    assert r1 == Rate(1000, 10).ratio
    assert r1 > Rate(200, 3).ratio
    assert r1 < Rate(200, 1).ratio


def test_create_rate_from_hits():
    hits = list(repeat(Hit(), 5))
    hits.extend(list(map(lambda hit: Hit(time=hit.time + 0.1), hits)))

    rate = Rate.create_from_hits(hits)
    assert rate.interval == 0.1
    assert rate.hits == 10
    assert rate.ratio == 100


def test_create_rate_from_no_hits():
    rate = Rate.create_from_hits([])
    assert rate.interval == 0
    assert rate.hits == 0
    assert rate.ratio == 0


def test_hit_ordering_seconds_precision():
    hit1 = Hit()
    hit2 = Hit()
    hit3 = Hit(time=hit1.time + 1)

    assert hit1 == hit2
    assert hit3 > hit1
    assert hit3 != hit2

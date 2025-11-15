from datetime import datetime, timezone, timedelta
import types
import pytest

from backend.rss_parser import RSSParser


def make_entry(title="T", link="L", summary="S", dt=None, use_updated=False):
    if dt is None:
        dt = datetime.now(timezone.utc)
    tm = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, 0, 0, 0)
    obj = types.SimpleNamespace()
    obj.title = title
    obj.link = link
    obj.summary = summary
    if use_updated:
        obj.updated_parsed = tm
    else:
        obj.published_parsed = tm
    return obj


class FakeFeed:
    def __init__(self, entries, bozo=False):
        self.entries = entries
        self.bozo = bozo


def test_parse_feed_includes_recent_entries_and_skips_old(monkeypatch):
    recent = make_entry(title="Recent", dt=datetime.now(timezone.utc) - timedelta(days=1))
    old = make_entry(title="Old", dt=datetime.now(timezone.utc) - timedelta(days=10))

    def fake_parse(url):
        return FakeFeed([recent, old])

    monkeypatch.setattr("backend.rss_parser.feedparser.parse", lambda url: fake_parse(url))

    parser = RSSParser()
    articles = parser.parse_feed("http://example.com/rss")

    assert len(articles) == 1
    assert articles[0]["title"] == "Recent"
    assert articles[0]["link"] == "L"
    assert isinstance(articles[0]["published_date"], datetime)


def test_parse_feed_uses_updated_when_no_published(monkeypatch):
    updated_only = make_entry(title="Updated", dt=datetime.now(timezone.utc) - timedelta(hours=2), use_updated=True)
    # remove published_parsed
    if hasattr(updated_only, "published_parsed"):
        delattr(updated_only, "published_parsed")

    def fake_parse(url):
        return FakeFeed([updated_only])

    monkeypatch.setattr("backend.rss_parser.feedparser.parse", lambda url: fake_parse(url))

    parser = RSSParser()
    articles = parser.parse_feed("http://example.com/rss")

    assert len(articles) == 1
    assert articles[0]["title"] == "Updated"


def test_parse_feed_gracefully_handles_missing_title(monkeypatch):
    e = make_entry(title="", dt=datetime.now(timezone.utc))

    def fake_parse(url):
        return FakeFeed([e])

    monkeypatch.setattr("backend.rss_parser.feedparser.parse", lambda url: fake_parse(url))

    parser = RSSParser()
    articles = parser.parse_feed("http://example.com/rss")

    assert articles == []


def test_parse_all_feeds_aggregates_and_sleeps_is_noop(monkeypatch):
    # Make feeds small and deterministic
    parser = RSSParser()
    parser.feeds = ["a", "b"]

    def fake_parse(url):
        return FakeFeed([make_entry(title=url)])

    monkeypatch.setattr("backend.rss_parser.feedparser.parse", lambda url: fake_parse(url))
    monkeypatch.setattr("backend.rss_parser.time.sleep", lambda s: None)

    articles = parser.parse_all_feeds()

    assert len(articles) == 2
    assert set(a["title"] for a in articles) == {"a", "b"}

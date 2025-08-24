import threading
from typing import Callable, Dict
from common.data import DataSource
from scraping.reddit.reddit_lite_scraper import RedditLiteScraper
from scraping.reddit.reddit_custom_scraper import RedditCustomScraper
from scraping.scraper import Scraper, ScraperId
from scraping.x.microworlds_scraper import MicroworldsTwitterScraper
from scraping.x.apidojo_scraper import ApiDojoTwitterScraper
from scraping.x.quacker_url_scraper import QuackerUrlScraper
from scraping.youtube.youtube_custom_scraper import YouTubeTranscriptScraper
from scraping.youtube.apify_youtube_scraper import YouTubeApifyTranscriptScraper
from scraping.custom.twikit_provider import TwikitProvider


DEFAULT_FACTORIES = {
    ScraperId.REDDIT_LITE: RedditLiteScraper,
    # For backwards compatibility with old configs, remap x.flash to x.apidojo.
    ScraperId.X_FLASH: MicroworldsTwitterScraper,
    ScraperId.REDDIT_CUSTOM: RedditCustomScraper,
    ScraperId.X_MICROWORLDS: lambda cfg, session: TwikitProvider(cfg, session),
    ScraperId.X_APIDOJO: ApiDojoTwitterScraper,
    ScraperId.X_QUACKER: QuackerUrlScraper,
    ScraperId.YOUTUBE_CUSTOM_TRANSCRIPT: YouTubeTranscriptScraper,
    ScraperId.YOUTUBE_APIFY_TRANSCRIPT : YouTubeApifyTranscriptScraper
}


class ScraperProvider:
    """A scraper provider will provide the correct scraper based on the source to be scraped."""

    def __init__(
        self, factories: Dict[DataSource, Callable[[], Scraper]] = DEFAULT_FACTORIES
    ):
        self.factories = factories

    def get(self, scraper_id: ScraperId, cfg=None, session=None) -> Scraper:
        """
        Returns a scraper for the given scraper id.
        If factory expects cfg and session, pass them through.
        """
        assert scraper_id in self.factories, f"Scraper id {scraper_id} not supported."
        factory = self.factories[scraper_id]
        try:
            # Попытаемся вызвать с аргументами
            return factory(cfg, session)
        except TypeError:
            # Если фабрика без аргументов — просто так
            return factory()


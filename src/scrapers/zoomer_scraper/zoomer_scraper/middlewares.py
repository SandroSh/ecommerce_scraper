import random
import time
import logging
from scrapy.downloadermiddlewares.retry import RetryMiddleware


class UserAgentMiddleware:
    """Rotate User-Agent strings to avoid detection"""

    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59'
        ]

    def process_request(self, request, spider):
        ua = random.choice(self.user_agents)
        request.headers['User-Agent'] = ua
        return None


class ProxyMiddleware:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Add your proxy list here
        self.proxies = [
            # 'http://proxy1:port',
            # 'http://proxy2:port',
        ]

    def process_request(self, request, spider):
        if self.proxies:
            proxy = random.choice(self.proxies)
            request.meta['proxy'] = proxy
            self.logger.debug(f"Using proxy: {proxy}")
        return None


class DelayMiddleware:
    """Add intelligent delays between requests"""

    def __init__(self, delay=1, randomize=True):
        self.delay = delay
        self.randomize = randomize
        self.last_request_time = 0

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        delay = settings.getfloat('DOWNLOAD_DELAY', 1)
        randomize = settings.getbool('RANDOMIZE_DOWNLOAD_DELAY', True)
        return cls(delay, randomize)

    def process_request(self, request, spider):
        current_time = time.time()
        elapsed = current_time - self.last_request_time

        if self.randomize:
            delay = random.uniform(self.delay * 0.5, self.delay * 1.5)
        else:
            delay = self.delay

        if elapsed < delay:
            time.sleep(delay - elapsed)

        self.last_request_time = time.time()
        return None


class CaptchaDetectionMiddleware:
    """Detect CAPTCHA challenges and handle appropriately"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.captcha_indicators = [
            'captcha',
            'recaptcha',
            'cloudflare',
            'human verification',
            'security check'
        ]

    def process_response(self, request, response, spider):
        # Check if response contains CAPTCHA indicators
        response_text = response.text.lower()

        for indicator in self.captcha_indicators:
            if indicator in response_text:
                self.logger.warning(f"CAPTCHA detected on {response.url}")

                # Save the page for manual inspection
                with open(f'captcha_page_{int(time.time())}.html', 'w') as f:
                    f.write(response.text)

                # Return None to retry the request
                return request.replace(dont_filter=True)

        return response


class CustomRetryMiddleware(RetryMiddleware):
    """Enhanced retry middleware with custom logic"""

    def __init__(self, settings):
        super().__init__(settings)
        self.logger = logging.getLogger(__name__)

    def retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1

        if retries <= self.max_retry_times:
            self.logger.info(f"Retrying {request.url} (attempt {retries}/{self.max_retry_times}): {reason}")

            # Add exponential backoff
            delay = 2 ** (retries - 1)
            time.sleep(delay)

            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True

            return retryreq
        else:
            self.logger.error(f"Gave up retrying {request.url} (failed {retries} times): {reason}")


class SessionMiddleware:
    """Maintain session cookies across requests"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_request(self, request, spider):
        # Ensure cookies are enabled for session maintenance
        request.meta['dont_merge_cookies'] = False
        return None

    def process_response(self, request, response, spider):
        # Log session-related cookies
        if 'Set-Cookie' in response.headers:
            self.logger.debug(f"Session cookies set for {response.url}")

        return response


class StatisticsMiddleware:
    """Collect scraping statistics"""

    def __init__(self, stats):
        self.stats = stats
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def spider_opened(self, spider):
        self.stats.set_value('start_time', time.time())

    def spider_closed(self, spider):
        end_time = time.time()
        start_time = self.stats.get_value('start_time', end_time)
        duration = end_time - start_time

        self.stats.set_value('duration', duration)
        self.logger.info(f"Spider {spider.name} finished in {duration:.2f} seconds")
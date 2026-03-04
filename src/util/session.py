import random

from requests import Response
from browserforge.fingerprints import FingerprintGenerator
from curl_cffi.requests import Session as RequestsSession

from src.core.logger import Logger
from src.settings import settings
from src.util.decorators import retry


class Session(RequestsSession):
    logger = Logger("Session")

    def __init__(self, proxy: list[str] = settings["PROXIES"]) -> None:
        super(Session, self).__init__()
        self.headers.update(self.generate_fingerprint())

        self.get('https://www.google.com/')  # we add some cookies so the session is not empty
        if isinstance(proxy, list):
            if isinstance(proxy, list): proxy = random.choice(proxy)
            self.proxies = {"https": proxy, "http": proxy}  # then we add the proxies after so we check proxies
            self.logger.info(f'proxy: {proxy} is implemented.')

        self.logger.debug('Session initialized successfully')

    def generate_fingerprint(self, user_agent: str = None) -> dict:
        fingerprint = FingerprintGenerator()
        headers = fingerprint.generate(user_agent=user_agent or self.headers.get('User-Agent')).headers
        return headers

    @retry
    def request(self, method, url, *args, **kwargs) -> Response:
        """accept http method and forward to parent"""
        kwargs.update({'timeout': 120, 'impersonate': "chrome99", 'verify': False})
        response: Response = super(Session, self).request(method=method, url=url, *args, **kwargs)
        if not response:
            self.logger.error(f'{method} request failed')
            return Response()
        return response

    def get(self, *args, **kwargs) -> Response:
        """ GET request with retry decorator """
        return self.request('GET', *args, **kwargs)

    def post(self, *args, **kwargs) -> Response:
        """ POST request with retry decorator """
        return self.request('POST', *args, **kwargs)


if __name__ == '__main__':
    from parsel import Selector
    from src.util.utils import clean_text

    session_ = Session()
    response_ = session_.get(url='https://www.browserscan.net/bot-detection')

    print(clean_text(Selector(response_.text).css('::text').extract()))
    print(response_.url)
    print(response_.status_code)
    print(response_.request.headers)

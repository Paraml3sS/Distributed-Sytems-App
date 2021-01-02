import random
import time


class RetryFactory:

    def __init__(self, config):

        self.retry_strategy = RandomizeRetryStrategyDecorator(
            self._get_retry_strategy(config)
        )

        if config.immediate_retry:
            self.retry_strategy = ImmediateRetryStrategyDecorator(self.retry_strategy)

    @staticmethod
    def _get_retry_strategy(config):
        if config.retry_strategy_name == 'exponential':
            return ExponentialRetryStrategy()
        elif config.retry_strategy_name == 'incremental':
            return IncrementalRetryStrategy()
        else:
            return RegularIntervalRetryStrategy(config.retry_delay)

    def build(self):
        return RetryDelayer(self.retry_strategy)


class RetryDelayer:
    def __init__(self, retry_strategy):
        self.retry_strategy = retry_strategy

    def delay(self):
        delay = self.retry_strategy.next()
        print(f"waiting for {delay} seconds")
        time.sleep(delay)


class RetryStrategy:
    def next(self):
        pass


class ImmediateRetryStrategyDecorator(RetryStrategy):

    def __init__(self, retry_strategy) -> None:
        self.retry_strategy = retry_strategy
        self.first_try = True

    def next(self):
        if self.first_try:
            self.first_try = False
            return 0
        else:
            return self.retry_strategy.next()


class RandomizeRetryStrategyDecorator(RetryStrategy):

    def __init__(self, retry_strategy) -> None:
        self.retry_strategy = retry_strategy
        self.range = 1

    def next(self):
        return self.retry_strategy.next() + self.random_number_milliseconds()

    def random_number_milliseconds(self):
        return random.random() * 2 * self.range - self.range

class RegularIntervalRetryStrategy(RetryStrategy):
    def __init__(self, delay):
        self.delay = delay

    def next(self):
        return self.delay


class ExponentialRetryStrategy(RetryStrategy):

    def __init__(self):
        self.maximum_backoff = 32
        self.a_try = -1

    def next(self):
        self.a_try += 1
        return min((2 ** self.a_try), self.maximum_backoff)


class IncrementalRetryStrategy(RetryStrategy):

    def __init__(self):
        self.maximum_backoff = 32
        self.a_try = -1
        self.basic_delay = 1
        self.increment = 3

    def next(self):
        self.a_try += 1
        return min(self.basic_delay + (self.a_try * self.increment), self.maximum_backoff)

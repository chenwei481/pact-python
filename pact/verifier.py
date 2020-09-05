"""Classes and methods to verify Contracts."""
from pact.verify_wrapper import VerifyWrapper, path_exists, expand_directories

class Verifier(object):
    """A Pact Verifier."""

    def __init__(self, provider, provider_base_url, **kwargs):
        """Create a new Verifier.

        Args:
            provider ([String]): provider name
            provider_base_url ([String]): provider url

        """
        self.provider = provider
        self.provider_base_url = provider_base_url

    def __str__(self):
        """Return string representation.

        Returns:
            [String]: verifier description.

        """
        return 'Verifier for {} with url {}'.format(self.provider, self.provider_base_url)

    def validate_publish(self, **kwargs):
        """Validate publish has a version."""
        if ((kwargs.get('publish') is not None) and (kwargs.get('publish_version') is None)):
            # do something
            raise Exception()

    def verify_pacts(self, *pacts, enable_pending=False, **kwargs):
        """Verify our pacts from the provider.

        Returns:
          success: True if no failures
          logs: some tbd output of logs

        """
        self.validate_publish(**kwargs)

        missing_files = [path for path in pacts if not path_exists(path)]
        if missing_files:
            raise Exception("Missing pact files {}".format(missing_files))

        pacts = expand_directories(pacts)
        missing_files = [path for path in pacts if not path_exists(path)]

        # rerun_command()  # env =

        options = self.extract_params(**kwargs)
        success, logs = VerifyWrapper().call_verify(*pacts,
                                                    provider=self.provider,
                                                    provider_base_url=self.provider_base_url,
                                                    enable_pending=enable_pending,
                                                    **options)

        return success, logs

    def verify_with_broker(self, enable_pending=False, **kwargs):
        """Use Broker to verify.

        Args:
            broker_username ([String]): broker username
            broker_password ([String]): broker password
            broker_url ([String]): url of broker
            enable_pending ([Boolean])

        """
        broker_username = kwargs.get('broker_username', None)
        broker_password = kwargs.get('broker_password', None)
        broker_url = kwargs.get('broker_url', None)
        broker_token = kwargs.get('broker_token', None)

        options = {
            'broker_password': broker_password,
            'broker_username': broker_username,
            'broker_token': broker_token,
            'broker_url': broker_url
        }
        options.update(self.extract_params(**kwargs))

        success, logs = VerifyWrapper().call_verify(provider=self.provider,
                                                    provider_base_url=self.provider_base_url,
                                                    enable_pending=enable_pending,
                                                    **options)
        return success, logs

    def extract_params(self, **kwargs):
        """Extract params."""
        log_dir = kwargs.get('log_dir', None)
        log_level = kwargs.get('log_level', 'INFO')
        provider_app_version = kwargs.get('provider_app_version', None)
        headers = kwargs.get('headers', [])
        timeout = kwargs.get('timeout', None)
        verbose = kwargs.get('verbose', None)
        consumer_tags = kwargs.get('consumer_tags', [])
        provider_tags = kwargs.get('provider_tags', [])
        states_setup_url = kwargs.get('provider_states_setup_url', None)
        verbose = kwargs.get('verbose', False)
        publish_version = kwargs.get('publish_version', None)

        options = {
            'log_dir': log_dir,
            'log_level': log_level,
            'provider_app_version': provider_app_version,
            'custom_provider_header': list(headers),
            'timeout': timeout,
            'verbose': verbose,
            'consumer_tags': list(consumer_tags),
            'provider_tags': list(provider_tags),
            'provider_states_setup_url': states_setup_url,
            'verbose': verbose,
            'publish_version': publish_version,
        }
        return self.filter_empty_options(**options)

    def filter_empty_options(self, **kwargs):
        """Filter out empty options."""
        kwargs = dict(filter(lambda item: item[1] is not None, kwargs.items()))
        kwargs = dict(filter(lambda item: item[1] != '', kwargs.items()))
        kwargs = dict(filter(lambda item: self.is_empty_list(item), kwargs.items()))
        return kwargs

    def is_empty_list(self, item):
        """Util for is empty lists."""
        return (not isinstance(item[1], list)) or (len(item[1]) != 0)

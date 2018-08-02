import click
import re

from web3 import Web3

from microraiden import Session
import logging
import requests


@click.command()
@click.option(
    '--private-key',
    required=True,
    help='Path to private key file or a hex-encoded private key.',
    type=click.Path(exists=True, dir_okay=False, resolve_path=True)
)
@click.option(
    '--password-path',
    default=None,
    help='Path to file containing the password for the private key specified.',
    type=click.Path(exists=True, dir_okay=False, resolve_path=True)
)
@click.option(
    '--receiver-url',
    default="http://localhost:5000",
    help='URL to the microraiden server, ie "http://localhost:5000".',
    type=str
)
@click.option('--resource', required=True, help='Get this resource.')
def main(
        private_key: str,
        password_path: str,
        resource: str,
        receiver_url: str
):
    run(private_key=private_key, password_path=password_path, resource=resource, endpoint_url=receiver_url)


def run(
        private_key: str,
        password_path: str,
        resource: str,
        channel_manager_address: str = None,
        web3: Web3 = None,
        retry_interval: float = 5,
        endpoint_url: str = 'http://localhost:5000'
):
    session = Session(
        endpoint_url=endpoint_url,
        private_key=private_key,
        key_password_path=password_path,
        channel_manager_address=channel_manager_address,
        web3=web3,
        retry_interval=retry_interval,
        initial_deposit=lambda x: x
    )
    stream_url = '{}/{}'.format(endpoint_url, resource)
    logging.info("Calling={}".format(stream_url))
    with session.get(stream_url, stream=True) as response:
        if response.status_code == requests.codes.OK:
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    print(line)
        else:
            logging.error(
                "Error getting the resource. Code={} body={}".format(
                    response.status_code,
                    response.text
                )
            )

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()

import logging
import os
import click
from flask import request
from web3 import Web3, HTTPProvider

from microraiden.channel_manager import ChannelManager
from microraiden.make_helpers import make_channel_manager
from microraiden.constants import WEB3_PROVIDER_DEFAULT
from microraiden.config import NETWORK_CFG
from microraiden.proxy import PaywalledProxy
from microraiden.proxy.resources import Expensive
from microraiden.utils import get_private_key
from alternate.ascii_resource import StreamResource, ProcessFrame
from microraiden.constants import TKN_DECIMALS

log = logging.getLogger(__name__)


@click.command()
@click.option(
    '--private-key',
    required=True,
    help='The server\'s private key path.',
    type=str
)
def main(private_key: str):
    private_key = get_private_key(private_key)
    run(private_key)


def run(
        private_key: str,
        state_file_path: str = os.path.join(click.get_app_dir('microraiden'), 'stream.db'),
        channel_manager: ChannelManager = None,
        join_thread: bool = True
):
    dirname = os.path.dirname(state_file_path)

    if dirname:
        os.makedirs(dirname, exist_ok=True)

    if channel_manager is None:
        web3 = Web3(HTTPProvider(WEB3_PROVIDER_DEFAULT))
        NETWORK_CFG.set_defaults(int(web3.version.network))
        channel_manager = make_channel_manager(
            private_key,
            NETWORK_CFG.CHANNEL_MANAGER_ADDRESS,
            state_file_path,
            web3
        )

    app = PaywalledProxy(channel_manager)

    app.add_paywalled_resource(StreamResource,
                               "/stream/<string:param>",
                               price = 1 * TKN_DECIMALS)

    app.run(host="localhost", port=5000, debug=True)

    if join_thread:
        app.join()
    else:
        return app


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
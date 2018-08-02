import click
import logging
from stream.ascii_resource import ProcessFrame, StreamResource
from microraiden.click_helpers import main, pass_app
from microraiden.constants import TKN_DECIMALS


@main.command()
@click.option(
    '--host',
    default='localhost',
    help='Address of the proxy'
)
@click.option(
    '--port',
    default=5000,
    help='Port of the proxy'
)
@pass_app
def start(app, host, port):
    # import pudb; pudb.set_trace()
    parrot_json = 'asciicast-113643.json'
    pf = ProcessFrame(parrot_json, offset=19)
    num_frames = 1000

    init_args = {
        'pf': pf,
        'num_frames': num_frames
    }
    app.add_paywalled_resource(StreamResource,
                               '/stream/<string:param>',
                               price= 3 * TKN_DECIMALS,
                               resource_class_kwargs = init_args)
    app.run(host=host, port=port, debug=True)
    app.join()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
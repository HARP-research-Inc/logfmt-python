from uuid import uuid4
import logging
import io
import pytest

@pytest.fixture
def setup_logger() -> tuple[logging.Logger, io.StringIO]:
    logger = logging.getLogger(str(uuid4()))
    logger.setLevel(logging.DEBUG)
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logger.addHandler(handler)
    return logger, stream
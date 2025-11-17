"""Application-wide extension instances."""
import os

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.getenv('RATE_LIMIT_STORAGE_URI', 'memory://'),
    strategy='moving-window',
    default_limits=[]
)


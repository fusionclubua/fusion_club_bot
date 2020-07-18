import sys

def fix_asyncio_event_loop_policy():
    if sys.platform.startswith("win") and sys.version_info >= (3, 8):
        import asyncio
        try:
            from asyncio import (
                WindowsProactorEventLoopPolicy,
                WindowsSelectorEventLoopPolicy,
            )
        except ImportError:
            pass
            # not affected
        else:
            if isinstance(asyncio.get_event_loop_policy(), WindowsProactorEventLoopPolicy):
                # WindowsProactorEventLoopPolicy is not compatible with tornado 6
                # fallback to the pre-3.8 default of Selector
                asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
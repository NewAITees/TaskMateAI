
def main():
    from . import server  # Import inside the function
    import asyncio
    return asyncio.run(server.main())


__all__ = ['main', 'server']



# No imports at the top level that could cause circularity


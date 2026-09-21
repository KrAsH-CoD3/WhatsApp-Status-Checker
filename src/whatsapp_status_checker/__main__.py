"""WhatsApp Status Checker - Main entry point"""

import sys

from .core import WhatsAppStatusChecker


def main() -> int:
    app = WhatsAppStatusChecker()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())

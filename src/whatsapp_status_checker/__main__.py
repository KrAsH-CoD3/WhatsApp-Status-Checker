"""WhatsApp Status Checker - Main entry point"""

from .core import WhatsAppStatusChecker


def main():
    app = WhatsAppStatusChecker()
    app.run()


if __name__ == "__main__":
    main()

"""
CONTINUOUS PIPELINE
Runs every 10 seconds to fetch web content and store in ChromaDB
"""

import time
import logging
from datetime import datetime
import signal
import sys
from typing import Optional
from chromadb_manager import ChromaDBManager
from web_scraper import WebScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContinuousPipeline:
    """
    Continuous pipeline that runs every N seconds
    """

    def __init__(
        self,
        interval_seconds: int = 10,
        persist_directory: str = "./chroma_db"
    ):
        self.interval = interval_seconds
        self.running = False
        self.iteration = 0
        self.total_documents_added = 0

        logger.info("🚀 Initializing Continuous Pipeline...")

        # Initialize components
        self.db_manager = ChromaDBManager(persist_directory=persist_directory)
        self.scraper = WebScraper()

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info(f"✅ Pipeline initialized (interval: {interval_seconds}s)")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info("\n🛑 Shutdown signal received")
        self.stop()

    def run_single_iteration(self) -> int:
        """
        Run one iteration of the pipeline

        Returns:
            Number of documents added
        """
        self.iteration += 1
        logger.info(f"\n{'='*80}")
        logger.info(f"🔄 Iteration {self.iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*80}")

        try:
            # Step 1: Fetch documents from web
            documents = self.scraper.fetch_all()

            if not documents:
                logger.warning("⚠️  No documents fetched")
                return 0

            # Step 2: Store in ChromaDB
            added = self.db_manager.add_documents(documents)

            self.total_documents_added += added

            # Step 3: Show stats
            stats = self.db_manager.get_stats()
            logger.info(f"\n📊 Pipeline Stats:")
            logger.info(f"   Iteration: {self.iteration}")
            logger.info(f"   Fetched this run: {len(documents)}")
            logger.info(f"   Added this run: {added}")
            logger.info(f"   Total in DB: {stats['total_documents']}")
            logger.info(f"   Total added (session): {self.total_documents_added}")

            if stats['sources']:
                logger.info(f"   Sources: {stats['sources']}")

            return added

        except Exception as e:
            logger.error(f"❌ Iteration {self.iteration} error: {e}")
            import traceback
            traceback.print_exc()
            return 0

    def start(self):
        """Start the continuous pipeline"""
        self.running = True

        logger.info("\n" + "="*80)
        logger.info("🚀 CONTINUOUS PIPELINE STARTED")
        logger.info("="*80)
        logger.info(f"⏰ Running every {self.interval} seconds")
        logger.info(f"🧠 Embedding model: all-mpnet-base-v2")
        logger.info(f"📁 Storage: {self.db_manager.client._settings.persist_directory}")
        logger.info(f"🌐 Sources: HackerNews, arXiv, GitHub, Medium, TechBlogs")
        logger.info("Press Ctrl+C to stop")
        logger.info("="*80 + "\n")

        while self.running:
            try:
                # Run iteration
                self.run_single_iteration()

                # Wait for next iteration
                if self.running:
                    logger.info(f"\n💤 Waiting {self.interval} seconds until next run...")
                    time.sleep(self.interval)

            except KeyboardInterrupt:
                logger.info("\n🛑 Keyboard interrupt received")
                self.stop()
                break

            except Exception as e:
                logger.error(f"❌ Pipeline error: {e}")
                import traceback
                traceback.print_exc()

                # Continue running on error
                if self.running:
                    logger.info(f"⚠️  Continuing... (waiting {self.interval}s)")
                    time.sleep(self.interval)

    def stop(self):
        """Stop the pipeline"""
        self.running = False

        logger.info("\n" + "="*80)
        logger.info("🛑 PIPELINE STOPPED")
        logger.info("="*80)
        logger.info(f"📊 Final Stats:")
        logger.info(f"   Total iterations: {self.iteration}")
        logger.info(f"   Total documents added: {self.total_documents_added}")

        stats = self.db_manager.get_stats()
        logger.info(f"   Final DB size: {stats['total_documents']}")
        logger.info("="*80 + "\n")

    def query_test(self, query: str, n_results: int = 3):
        """Test query against ChromaDB"""
        logger.info(f"\n🔍 Testing query: '{query}'")

        results = self.db_manager.query(query, n_results=n_results)

        if not results['documents']:
            logger.info("   No results found")
            return

        logger.info(f"   Found {len(results['documents'])} results:\n")

        for i, (doc, dist, meta) in enumerate(zip(
            results['documents'],
            results['distances'],
            results['metadatas']
        ), 1):
            logger.info(f"   {i}. [{meta['source']}] {meta.get('title', 'No title')}")
            logger.info(f"      Distance: {dist:.4f}")
            logger.info(f"      URL: {meta.get('url', 'N/A')}")
            logger.info(f"      Preview: {doc[:150]}...")
            logger.info("")


class InteractivePipeline:
    """
    Interactive mode for testing and monitoring
    """

    def __init__(self):
        self.pipeline = None

    def show_menu(self):
        """Show interactive menu"""
        print("\n" + "="*80)
        print("🤖 CONTINUOUS PIPELINE - INTERACTIVE MODE")
        print("="*80)
        print("\nOptions:")
        print("  1. Start pipeline (10 second interval)")
        print("  2. Start pipeline (custom interval)")
        print("  3. Run single iteration")
        print("  4. Query ChromaDB")
        print("  5. Show stats")
        print("  6. Reset database")
        print("  0. Exit")
        print("="*80)

    def run(self):
        """Run interactive mode"""
        self.pipeline = ContinuousPipeline(interval_seconds=10)

        while True:
            self.show_menu()
            choice = input("\nEnter choice: ").strip()

            if choice == '1':
                self.pipeline.start()

            elif choice == '2':
                interval = int(input("Enter interval (seconds): "))
                self.pipeline = ContinuousPipeline(interval_seconds=interval)
                self.pipeline.start()

            elif choice == '3':
                added = self.pipeline.run_single_iteration()
                print(f"\n✅ Added {added} documents")
                input("\nPress Enter to continue...")

            elif choice == '4':
                query = input("Enter query: ")
                n_results = int(input("Number of results (default 3): ") or "3")
                self.pipeline.query_test(query, n_results)
                input("\nPress Enter to continue...")

            elif choice == '5':
                stats = self.pipeline.db_manager.get_stats()
                print("\n📊 Stats:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                input("\nPress Enter to continue...")

            elif choice == '6':
                confirm = input("⚠️  Reset database? (yes/no): ")
                if confirm.lower() == 'yes':
                    self.pipeline.db_manager.reset()
                    print("✅ Database reset")
                input("\nPress Enter to continue...")

            elif choice == '0':
                print("\n👋 Goodbye!")
                break

            else:
                print("❌ Invalid choice")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Continuous Web Content Pipeline')
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='Interval in seconds between iterations (default: 10)'
    )
    parser.add_argument(
        '--persist-dir',
        type=str,
        default='./chroma_db',
        help='ChromaDB persistence directory (default: ./chroma_db)'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit'
    )

    args = parser.parse_args()

    if args.interactive:
        # Interactive mode
        interactive = InteractivePipeline()
        interactive.run()

    elif args.once:
        # Run once
        pipeline = ContinuousPipeline(
            interval_seconds=args.interval,
            persist_directory=args.persist_dir
        )
        added = pipeline.run_single_iteration()
        print(f"\n✅ Added {added} documents")
        stats = pipeline.db_manager.get_stats()
        print(f"📊 Total in DB: {stats['total_documents']}")

    else:
        # Continuous mode
        pipeline = ContinuousPipeline(
            interval_seconds=args.interval,
            persist_directory=args.persist_dir
        )
        pipeline.start()


if __name__ == "__main__":
    main()

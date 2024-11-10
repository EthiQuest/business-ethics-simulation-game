#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MigrationManager:
    """Manages database migrations"""

    def __init__(self):
        self.alembic_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'alembic'
        )
        self.versions_dir = os.path.join(self.alembic_dir, 'versions')

    def _run_alembic_command(self, command: list) -> bool:
        """Run an alembic command"""
        try:
            result = subprocess.run(
                ['alembic'] + command,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Command failed: {result.stderr}")
                return False
                
            logger.info(result.stdout)
            return True
            
        except Exception as e:
            logger.error(f"Error running alembic command: {str(e)}")
            return False

    def create_migration(self, name: str) -> bool:
        """Create a new migration"""
        try:
            # Format timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            
            # Create migration file
            command = [
                'revision',
                '--autogenerate',
                '-m',
                f"{timestamp}_{name}"
            ]
            
            success = self._run_alembic_command(command)
            
            if success:
                logger.info(f"Created new migration: {timestamp}_{name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error creating migration: {str(e)}")
            return False

    def upgrade_database(self, revision: str = 'head') -> bool:
        """Upgrade database to specified revision"""
        try:
            command = ['upgrade', revision]
            success = self._run_alembic_command(command)
            
            if success:
                logger.info(f"Database upgraded to: {revision}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error upgrading database: {str(e)}")
            return False

    def downgrade_database(self, revision: str = '-1') -> bool:
        """Downgrade database to specified revision"""
        try:
            command = ['downgrade', revision]
            success = self._run_alembic_command(command)
            
            if success:
                logger.info(f"Database downgraded to: {revision}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error downgrading database: {str(e)}")
            return False

    def show_history(self) -> bool:
        """Show migration history"""
        try:
            command = ['history']
            return self._run_alembic_command(command)
            
        except Exception as e:
            logger.error(f"Error showing history: {str(e)}")
            return False

    def show_current(self) -> bool:
        """Show current revision"""
        try:
            command = ['current']
            return self._run_alembic_command(command)
            
        except Exception as e:
            logger.error(f"Error showing current revision: {str(e)}")
            return False

    def check_migrations(self) -> bool:
        """Check if all migrations are applied"""
        try:
            command = ['check']
            return self._run_alembic_command(command)
            
        except Exception as e:
            logger.error(f"Error checking migrations: {str(e)}")
            return False

def main():
    """Main function for migration management"""
    parser = argparse.ArgumentParser(
        description='Manage database migrations'
    )
    
    parser.add_argument(
        'action',
        choices=[
            'create',
            'upgrade',
            'downgrade',
            'history',
            'current',
            'check'
        ],
        help='Action to perform'
    )
    
    parser.add_argument(
        '--name',
        help='Name for new migration (required for create)'
    )
    
    parser.add_argument(
        '--revision',
        help='Target revision (for upgrade/downgrade)'
    )

    args = parser.parse_args()
    manager = MigrationManager()

    if args.action == 'create':
        if not args.name:
            logger.error("Name is required for create action")
            sys.exit(1)
        success = manager.create_migration(args.name)
        
    elif args.action == 'upgrade':
        revision = args.revision or 'head'
        success = manager.upgrade_database(revision)
        
    elif args.action == 'downgrade':
        revision = args.revision or '-1'
        success = manager.downgrade_database(revision)
        
    elif args.action == 'history':
        success = manager.show_history()
        
    elif args.action == 'current':
        success = manager.show_current()
        
    elif args.action == 'check':
        success = manager.check_migrations()

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
BeautyBooking Configuration Checker
Utility script for validating project configuration before deployment.
"""

import argparse
import sys
import os
from pathlib import Path
import requests
from colorama import Fore, Style, init
from dotenv import load_dotenv

# Initialize colorama for Windows
init()

# Load environment variables from .env file
load_dotenv()


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='BeautyBooking Configuration Checker - validates project setup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python beauty_check.py --project-path "C:/Projects/beauty_salon"
  python beauty_check.py -p "C:/Projects/beauty_salon" --check-db --verbose
        '''
    )
    
    parser.add_argument(
        '-p', '--project-path',
        type=str,
        required=True,
        help='Path to the BeautyBooking project directory (required)'
    )
    
    parser.add_argument(
        '--check-db',
        action='store_true',
        help='Check PostgreSQL database connection'
    )
    
    parser.add_argument(
        '--check-api',
        action='store_true',
        help='Check API endpoint availability'
    )
    
    parser.add_argument(
        '--api-url',
        type=str,
        default='http://localhost:8000',
        help='API base URL (default: http://localhost:8000)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output with detailed information'
    )
    
    return parser.parse_args()


def check_project_structure(project_path: str, verbose: bool = False) -> bool:
    """Check if required project files and directories exist"""
    required_items = [
        'manage.py',
        'beauty_salon/settings.py',
        'booking/models.py',
        'requirements.txt',
        'static/',
        'media/'
    ]
    
    print(f"{Fore.CYAN}📁 Checking project structure at: {project_path}{Style.RESET_ALL}")
    
    all_exist = True
    for item in required_items:
        item_path = Path(project_path) / item
        exists = item_path.exists()
        status = f"{Fore.GREEN}✓{Style.RESET_ALL}" if exists else f"{Fore.RED}✗{Style.RESET_ALL}"
        print(f"  {status} {item}")
        if not exists:
            all_exist = False
            if verbose:
                print(f"    {Fore.YELLOW}Warning: {item} not found{Style.RESET_ALL}")
    
    return all_exist


def check_database_connection(verbose: bool = False) -> bool:
    """Check PostgreSQL database connectivity"""
    print(f"\n{Fore.CYAN}🗄️  Checking database connection...{Style.RESET_ALL}")
    
    db_name = os.getenv('DB_NAME', 'beauty_salon_db')
    db_user = os.getenv('DB_USER', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    
    if verbose:
        print(f"  Host: {db_host}:{db_port}")
        print(f"  Database: {db_name}")
        print(f"  User: {db_user}")
    
    try:
        print(f"  {Fore.GREEN}✓ Database connection parameters validated{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"  {Fore.RED}✗ Database connection failed: {e}{Style.RESET_ALL}")
        return False


def check_api_endpoint(api_url: str, verbose: bool = False) -> bool:
    """Check if API endpoint is reachable"""
    print(f"\n{Fore.CYAN}🌐 Checking API endpoint: {api_url}{Style.RESET_ALL}")
    
    try:
        response = requests.get(f"{api_url}/api/health/", timeout=5)
        if response.status_code == 200:
            print(f"  {Fore.GREEN}✓ API is healthy (status: {response.status_code}){Style.RESET_ALL}")
            return True
        else:
            print(f"  {Fore.YELLOW}⚠ API returned status: {response.status_code}{Style.RESET_ALL}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  {Fore.RED}✗ Cannot connect to API at {api_url}{Style.RESET_ALL}")
        return False
    except requests.exceptions.Timeout:
        print(f"  {Fore.RED}✗ Request timed out{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"  {Fore.RED}✗ Error: {e}{Style.RESET_ALL}")
        return False


def print_summary(structure_ok: bool, db_ok: bool, api_ok: bool):
    """Print final summary"""
    print(f"\n{Fore.BLUE}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}📊 CONFIGURATION CHECK SUMMARY{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'='*50}{Style.RESET_ALL}")
    
    results = [
        ("Project Structure", structure_ok),
        ("Database Connection", db_ok),
        ("API Endpoint", api_ok)
    ]
    
    all_passed = True
    for name, passed in results:
        status = f"{Fore.GREEN}PASS{Style.RESET_ALL}" if passed else f"{Fore.RED}FAIL{Style.RESET_ALL}"
        print(f"  {name:.<35} {status}")
        if not passed:
            all_passed = False
    
    print(f"{Fore.BLUE}{'='*50}{Style.RESET_ALL}")
    
    if all_passed:
        print(f"{Fore.GREEN}✅ All checks passed! Project is ready for deployment.{Style.RESET_ALL}")
        return 0
    else:
        print(f"{Fore.RED}❌ Some checks failed. Please review the output above.{Style.RESET_ALL}")
        return 1


def main():
    """Main entry point"""
    args = parse_arguments()
    
    print(f"{Fore.BLUE}🚀 BeautyBooking Configuration Checker v1.0{Style.RESET_ALL}\n")
    
    structure_ok = check_project_structure(args.project_path, args.verbose)
    
    db_ok = True
    if args.check_db:
        db_ok = check_database_connection(args.verbose)
    
    api_ok = True
    if args.check_api:
        api_ok = check_api_endpoint(args.api_url, args.verbose)
    
    exit_code = print_summary(structure_ok, db_ok, api_ok)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

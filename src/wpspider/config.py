import json
import os
import argparse
import re
from typing import List, Optional
from urllib.parse import urlparse

DEFAULT_ENDPOINTS = [
    "categories",
    "comments",
    "media",
    "pages",
    "posts",
    "tags",
    "users"
]

class Config:
    def __init__(self, config_path: str = "config.json", args: Optional[argparse.Namespace] = None):
        self.config_path = config_path
        self.target: Optional[str] = None
        self.endpoints: List[str] = DEFAULT_ENDPOINTS
        self.db_name: Optional[str] = None
        self.output_directory: Optional[str] = None
        self.user_agent: str = "WPSpider/1.0 (Nebula Crawler; +https://wpspider.local)"
        self.log_file: str = "wpspider.log"
        
        # Load from file
        self._load_from_file()
        
        # Override with args
        if args:
            self._apply_args(args)
            
        # Validation
        self.validate()

    def _load_from_file(self):
        if not os.path.exists(self.config_path):
            # If config file doesn't exist, we rely on defaults or args
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.target = data.get("target", self.target)
            self.endpoints = data.get("endpoints", self.endpoints)
            self.db_name = data.get("db_name", data.get("output", self.db_name))
            self.output_directory = data.get("output_directory", data.get("directory", self.output_directory))
            self.user_agent = data.get("user_agent", self.user_agent)
            self.log_file = data.get("log_file", self.log_file)
            
        except json.JSONDecodeError:
            print(f"Warning: Could not decode {self.config_path}. Using defaults.")
        except Exception as e:
            print(f"Warning: Error reading {self.config_path}: {e}")

    def _apply_args(self, args: argparse.Namespace):
        if hasattr(args, 'target') and args.target:
            self.target = args.target
        
        if hasattr(args, 'output') and args.output:
            self.db_name = args.output

        if hasattr(args, 'directory') and args.directory:
            self.output_directory = args.directory

        if hasattr(args, 'user_agent') and args.user_agent:
            self.user_agent = args.user_agent
            
        # Add more arg overrides as needed

    def validate(self):
        if not self.target:
            raise ValueError("Configuration Error: 'target' URL is required. Please provide it via the --target command-line argument.")

        self.target = self._normalize_target(self.target)
        
        if not self.endpoints:
            raise ValueError("Configuration Error: No endpoints specified.")

        # Resolve output path
        if self.db_name and self.output_directory:
            # Mutually exclusive: output file wins
            print("Warning: Both output file and output directory specified; using output file and ignoring output directory.")

        if not self.db_name:
            self.db_name = self._derive_output_path(self.target, self.output_directory)

    @staticmethod
    def _normalize_target(target: str) -> str:
        normalized = target.strip()
        if not normalized:
            return normalized

        if normalized.startswith("//"):
            normalized = f"https:{normalized}"

        parsed = urlparse(normalized)
        if not parsed.scheme:
            normalized = f"https://{normalized}"

        return normalized

    @staticmethod
    def _sanitize_domain(domain: str) -> str:
        if not domain:
            return "target"
        # Replace invalid filename chars with underscore
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", domain)
        return safe.strip("._") or "target"

    @classmethod
    def _derive_output_path(cls, target: str, output_directory: Optional[str]) -> str:
        parsed = urlparse(target)
        domain = parsed.netloc or parsed.path.split('/')[0]
        domain = domain.replace(":", "_")
        safe_domain = cls._sanitize_domain(domain)
        filename = f"{safe_domain}.sqlite"

        base_dir = output_directory if output_directory is not None else os.getcwd()
        return os.path.join(base_dir, filename)

    def __repr__(self):
        return f"<Config target={self.target} db={self.db_name} endpoints={len(self.endpoints)}>"

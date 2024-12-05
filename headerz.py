#!/bin/python3
#Author: avacadoPWN (Kovan MohammedAmeen)
#License: MIT

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse, urljoin
import aiohttp
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from pydantic import BaseModel, HttpUrl


@dataclass
class Stats:
    num_of_requests: int = 0
    passed: int = 0
    ssl_error: int = 0
    error: int = 0
    num_of_urls: int = 0

class HeaderData(BaseModel):
    domain: str
    url: HttpUrl
    headers: Dict[str, str]

class Config(BaseModel):
    urls_list: Path
    json_export: Optional[Path]
    num_threads: int = 65
    timeout: int = 10
    concurrent_limit: int = 100

class HeaderCollector:
    def __init__(self, config: Config):
        self.config = config
        self.stats = Stats()
        self.collected_data: Dict[str, Dict] = {}
        self.console = Console()
        
    async def process_url(self, url: str, semaphore: asyncio.Semaphore) -> None:
        if not url.strip():
            self.stats.num_of_requests -= 1
            return

        url = self._normalize_url(url)
        
        async with semaphore:
            try:
                timeout = aiohttp.ClientTimeout(total=self.config.timeout)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.head(url, ssl=False) as response:
                        headers = dict(response.headers)
                        self._add_to_dict(url, str(response.url), headers)
                        self.stats.passed += 1
                        
            except aiohttp.ClientSSLError:
                self.stats.ssl_error += 1
            except Exception:
                self.stats.error += 1
            finally:
                self.stats.num_of_requests += 1

    def _normalize_url(self, url: str) -> str:
        if not any(url.startswith(prefix) for prefix in ['http://', 'https://']):
            url = f"https://{url}"
        parsed = urlparse(url)
        if not parsed.path:
            url = f"{url}/"
        return url

    def _add_to_dict(self, original_url: str, dest_url: str, headers: Dict[str, str]) -> None:
        self.collected_data[original_url] = {
            'url': dest_url,
            'headers': headers
        }

    async def process_urls(self, urls: List[str]) -> None:
        self.stats.num_of_urls = len(urls)
        semaphore = asyncio.Semaphore(self.config.concurrent_limit)
        
        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]Processing URLs...", total=len(urls))
            tasks = [self.process_url(url, semaphore) for url in urls]
            for coro in asyncio.as_completed(tasks):
                await coro
                progress.update(task, advance=1)

    def export_results(self) -> None:
        self.console.print("\nExporting collected headers to NDJSON...")
        with Progress(console=self.console) as progress:
            task = progress.add_task("[green]Exporting...", total=len(self.collected_data))
            
            with self.config.json_export.open('a+') as f:
                for domain, data in self.collected_data.items():
                    header_data = {
                        'domain': domain,
                        'url': str(data['url']),  # Convert URL to string
                        'headers': data['headers']
                    }
                    f.write(f"{json.dumps(header_data)}\n")
                    progress.update(task, advance=1)

app = typer.Typer()

@app.command()
def main(
    urls_list: Path = typer.Argument(..., help="File containing list of URLs"),
    json_export: Optional[Path] = typer.Option(
        None, help="Output file for JSON results"
    ),
    num_threads: int = typer.Option(
        65, help="Number of concurrent threads", min=1, max=250
    ),
    timeout: int = typer.Option(
        10, help="Timeout in seconds for each request"
    ),
    concurrent_limit: int = typer.Option(
        100, help="Maximum number of concurrent connections"
    )
) -> None:
    """Collect HTTP headers from a list of URLs."""
    console = Console()
    
    if not urls_list.exists():
        console.print(f"\n[red]Error[/red]: URL list '{urls_list}' not found!")
        raise typer.Exit(1)

    if not json_export:
        json_export = Path(f"{urls_list.stem}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.ndjson")

    config = Config(
        urls_list=urls_list,
        json_export=json_export,
        num_threads=num_threads,
        timeout=timeout,
        concurrent_limit=concurrent_limit
    )

    collector = HeaderCollector(config)
    urls = urls_list.read_text().splitlines()

    start_time = datetime.now()
    asyncio.run(collector.process_urls(urls))
    
    console.print("\nStats:", style="bold")
    console.print(collector.stats)
    
    collector.export_results()
    
    elapsed = (datetime.now() - start_time).total_seconds()
    console.print(f"\n[green]All done.[/green]")
    console.print(f"Time Elapsed: {elapsed:.2f}s")

if __name__ == "__main__":
    app()


"""CLI interface for the Complex Word Finder."""

import asyncio
import click
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from .models import AnalysisConfig, OutputFormat
from .analyzer import ComplexWordAnalyzer
from .output_handler import OutputHandler


console = Console()


@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--min-syllables', '-m', default=3, help='Minimum number of syllables to consider a word polysyllabic (default: 3)')
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output file to save results')
@click.option('--synonyms/--no-synonyms', default=True, help='Find synonyms for polysyllabic words (default: enabled)')
@click.option('--limit', '-l', type=int, help='Limit the number of words to process')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'csv']), default='table', help='Output format')
def main(input_file: Path, min_syllables: int, output: Path, synonyms: bool, limit: int, output_format: str):
    """
    Analyze Brazilian Portuguese text to find polysyllabic words, count syllables, and find synonyms.
    
    INPUT_FILE: Path to the text file to analyze
    """
    asyncio.run(_async_main(input_file, min_syllables, output, synonyms, limit, output_format))


async def _async_main(input_file: Path, min_syllables: int, output: Path, synonyms: bool, limit: int, output_format: str):
    """Async version of the main function."""
    _display_header()
    
    try:
        # Create configuration
        config = AnalysisConfig(
            min_syllables=min_syllables,
            find_synonyms=synonyms,
            limit=limit,
            output_format=OutputFormat(output_format)
        )
        
        # Read text
        text = _read_input_file(input_file)
        
        # Perform analysis
        analyzer = ComplexWordAnalyzer(console)
        results = await analyzer.analyze_text(text, config)
        
        # Handle empty results
        if not results.word_data:
            console.print(f"[yellow]No polysyllabic words found with {min_syllables}+ syllables[/yellow]")
            return
        
        # Display and save results
        output_handler = OutputHandler(console)
        output_handler.display_results(results)
        
        if output:
            output_handler.save_results(results, output)
        
        output_handler.display_summary(results)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def _display_header():
    """Display application header."""
    console.print(Panel.fit(
        "[bold blue]Complex Word Finder[/bold blue]\n"
        "Analyzing Brazilian Portuguese text for polysyllabic words",
        border_style="blue"
    ))


def _read_input_file(input_file: Path) -> str:
    """Read and return text content from input file."""
    console.print(f"📖 Reading text from: [cyan]{input_file}[/cyan]")
    return input_file.read_text(encoding='utf-8')


if __name__ == "__main__":
    main()
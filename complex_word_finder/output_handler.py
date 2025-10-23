"""Output formatting and file handling."""

import json
from pathlib import Path
from io import StringIO
from typing import List, Tuple
from rich.console import Console
from rich.table import Table

from .models import AnalysisResults, OutputFormat, WordData


class OutputHandler:
    """Handles result display and file output."""

    def __init__(self, console: Console):
        self.console = console

    def display_results(self, results: AnalysisResults):
        """Display analysis results in the configured format."""
        format_handlers = {
            OutputFormat.TABLE: self._display_table,
            OutputFormat.JSON: self._display_json,
            OutputFormat.CSV: self._display_csv,
        }

        handler = format_handlers[results.config.output_format]
        handler(results.sorted_words)

    def save_results(self, results: AnalysisResults, output_path: Path):
        """Save results to file."""
        format_handlers = {
            OutputFormat.JSON: self._save_json,
            OutputFormat.CSV: self._save_csv,
            OutputFormat.TABLE: self._save_table,
        }

        try:
            handler = format_handlers[results.config.output_format]
            content = handler(results.sorted_words)
            output_path.write_text(content, encoding="utf-8")
            self.console.print(f"💾 Results saved to: [cyan]{output_path}[/cyan]")
        except Exception as e:
            self.console.print(f"[red]Error saving file: {e}[/red]")

    def display_summary(self, results: AnalysisResults):
        """Display analysis summary."""
        self.console.print("\n📈 [bold]Summary:[/bold]")
        self.console.print(
            f"   • Polysyllabic words found: [green]{results.polysyllabic_words}[/green]"
        )
        self.console.print(
            f"   • Total occurrences: [green]{results.total_occurrences}[/green]"
        )
        self.console.print(
            f"   • Minimum syllables: [green]{results.config.min_syllables}[/green]"
        )
        
        # Show pagination info if offset or limit is used
        displayed_count = len(results.sorted_words)
        if results.config.offset > 0 or results.config.limit:
            start_num = results.config.offset + 1
            end_num = results.config.offset + displayed_count
            self.console.print(f"   • Showing words [cyan]{start_num}-{end_num}[/cyan] of [cyan]{results.polysyllabic_words}[/cyan]")
            
            if results.config.limit and (results.config.offset + results.config.limit) < results.polysyllabic_words:
                next_offset = results.config.offset + results.config.limit
                self.console.print(f"   • [dim]Use --offset {next_offset} to see more results[/dim]")

    def _display_table(self, sorted_words: List[Tuple[str, WordData]]):
        """Display results as a formatted table."""
        table = Table(title="Polysyllabic Words Analysis")
        table.add_column("Word", style="cyan", no_wrap=True)
        table.add_column("Syllables", justify="right", style="magenta")
        table.add_column("Count", justify="right", style="green")
        table.add_column("Synonyms", style="yellow")

        for word, data in sorted_words:
            synonyms_display = self._format_synonyms_for_display(data.synonyms)
            table.add_row(word, str(data.syllables), str(data.count), synonyms_display)

        self.console.print(table)

    def _display_json(self, sorted_words: List[Tuple[str, WordData]]):
        """Display results as JSON."""
        result = {
            word: {
                "syllables": data.syllables,
                "count": data.count,
                "synonyms": data.synonyms,
            }
            for word, data in sorted_words
        }
        self.console.print(json.dumps(result, indent=2, ensure_ascii=False))

    def _display_csv(self, sorted_words: List[Tuple[str, WordData]]):
        """Display results as CSV."""
        self.console.print("Word,Syllables,Count,Synonyms")
        for word, data in sorted_words:
            synonyms_str = "|".join(data.synonyms)
            self.console.print(
                f'"{word}",{data.syllables},{data.count},"{synonyms_str}"'
            )

    def _save_json(self, sorted_words: List[Tuple[str, WordData]]) -> str:
        """Generate JSON content for saving."""
        result = {
            word: {
                "syllables": data.syllables,
                "count": data.count,
                "synonyms": data.synonyms,
            }
            for word, data in sorted_words
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    def _save_csv(self, sorted_words: List[Tuple[str, WordData]]) -> str:
        """Generate CSV content for saving."""
        lines = ["Word,Syllables,Count,Synonyms"]
        for word, data in sorted_words:
            synonyms_str = "|".join(data.synonyms)
            lines.append(f'"{word}",{data.syllables},{data.count},"{synonyms_str}"')
        return "\n".join(lines)

    def _save_table(self, sorted_words: List[Tuple[str, WordData]]) -> str:
        """Generate table content for saving."""
        buffer = StringIO()
        file_console = Console(file=buffer, width=120)

        # Create table for file output
        table = Table(title="Polysyllabic Words Analysis")
        table.add_column("Word", no_wrap=True)
        table.add_column("Syllables", justify="right")
        table.add_column("Count", justify="right")
        table.add_column("Synonyms")

        for word, data in sorted_words:
            synonyms_display = self._format_synonyms_for_display(data.synonyms)
            table.add_row(word, str(data.syllables), str(data.count), synonyms_display)

        file_console.print(table)
        return buffer.getvalue()

    def _format_synonyms_for_display(self, synonyms: List[str]) -> str:
        """Format synonyms for display with truncation and syllable info."""
        if not synonyms:
            return "-"

        # Import here to avoid circular imports
        from .word_analyzer import WordAnalyzer

        analyzer = WordAnalyzer()

        # Format synonyms with syllable counts
        formatted_synonyms = []
        for synonym in synonyms[:3]:
            syllable_count = analyzer.count_syllables(synonym)
            formatted_synonyms.append(f"{synonym}({syllable_count})")

        formatted_synonyms.sort(key=lambda s: len(s))
        result = ", ".join(formatted_synonyms)

        if len(synonyms) > 3:
            result += "..."

        return result

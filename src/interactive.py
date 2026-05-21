import webbrowser
from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static, Markdown
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.binding import Binding
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text

class SourceBadge(Static):
    """A small badge for the source."""
    def __init__(self, source: str):
        super().__init__()
        self.source = source.lower()
        
    def render(self):
        source_map = {
            "hacker news": ("[bold orange]HN[/bold orange]", "orange"),
            "reddit": ("[bold red]RED[/bold red]", "red"),
            "arxiv": ("[bold blue]ARX[/bold blue]", "blue"),
            "github": ("[bold white]GIT[/bold white]", "white"),
            "dev.to": ("[bold cyan]DEV[/bold cyan]", "cyan")
        }
        text, color = source_map.get(self.source, (f"[bold]{self.source[:3].upper()}[/bold]", "white"))
        return f"[{text}]"

class DetailPanel(ScrollableContainer):
    """A panel to show details of a tech item."""
    
    def update_content(self, item: dict):
        self.remove_children()
        
        # Title
        self.mount(Label(f"\n[bold]{item.get('title')}[/bold]\n"))
        
        # Source badge color
        source_name = item.get('source', 'Unknown')
        source_lower = source_name.lower()
        source_color = "orange" if "hacker" in source_lower else "red" if "reddit" in source_lower else "blue" if "arxiv" in source_lower else "white" if "github" in source_lower else "cyan" if "dev" in source_lower else "white"
        
        # Category color
        cat_colors = {
            "AI/ML": "magenta",
            "DevTools": "blue",
            "Security": "red",
            "Web": "cyan",
            "Systems": "yellow",
            "Research": "purple",
            "Other": "white"
        }
        cat = item.get('category', 'Other')
        cat_color = cat_colors.get(cat, 'white')

        # Importance Bar
        try:
            val = int(float(item.get('importance', 0)))
        except (ValueError, TypeError):
            val = 0
        # Use basic block characters for universal support
        bar = "X" * val + "-" * (10 - val)
        
        metadata = Text.assemble(
            ("Source: ", "dim"), (source_name, f"bold {source_color}"),
            (" | ", "dim"),
            ("Category: ", "dim"), (cat, f"bold {cat_color}"),
            ("\nImportance: ", "dim"), (f"[{bar}]", "bold green"), (f" {item.get('importance')}/10", "bold")
        )
        self.mount(Static(metadata))

        # Summary
        summary_md = f"""
## Summary
{item.get('summary')}

---
**URL:** [{item.get('url')}]({item.get('url')})
**Date:** {item.get('date', datetime.now().strftime('%Y-%m-%d'))}
"""
        self.mount(Markdown(summary_md))
        
        # Footer help
        self.mount(Static("\n[Press 'O' to open in browser]", classes="help-text"))

class TechItem(ListItem):
    """A list item representing a tech development."""
    def __init__(self, item: dict):
        super().__init__()
        self.item = item
        
    def compose(self) -> ComposeResult:
        source = self.item.get('source', '').lower()
        # Case-insensitive partial matching for badges
        if "hacker" in source or "hn" in source: badge = "HN"
        elif "reddit" in source or "red" in source: badge = "RED"
        elif "arxiv" in source or "arx" in source: badge = "ARX"
        elif "github" in source or "git" in source: badge = "GIT"
        elif "dev.to" in source or "dev" in source: badge = "DEV"
        else: badge = source[:3].upper() if source else "???"
        
        rank = self.item.get('rank', '-')
        title = self.item.get('title', 'No Title')
        imp = self.item.get('importance', 0)
        
        yield Label(f"{rank:>2} [{badge}] {title[:50] + '...' if len(title) > 50 else title} ({imp}/10)")

class ToggleItem(ListItem):
    """A special list item to toggle between Top 20 and Show All."""
    def __init__(self, show_all: bool):
        super().__init__()
        self.show_all = show_all
        
    def compose(self) -> ComposeResult:
        label = "[ Show Top 20 ]" if self.show_all else "[ Show All Results ]"
        yield Label(label, id="toggle-label")

class TechRadarApp(App):
    """An interactive dashboard for tech radar."""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 2fr;
    }

    .help-text {
        color: $text-disabled;
        text-style: italic;
    }

    #list-container {
        border-right: solid $accent;
        height: 100%;
        layout: vertical;
    }

    #detail-container {
        height: 100%;
        padding: 1;
    }

    ListItem {
        padding: 0 1;
        height: 1;
    }

    ListItem:hover {
        background: $accent;
    }

    .selected {
        background: $accent-darken-2;
        text-style: bold;
    }
    
    #toggle-label {
        width: 100%;
        text-align: center;
        color: $accent;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("escape", "quit", "Quit", show=False),
        Binding("f", "cycle_filter", "Filter Category", show=True),
        Binding("s", "toggle_mode", "Toggle Top 20/All", show=True),
        Binding("o", "open_url", "Open URL", show=True),
    ]

    show_all = reactive(False)
    current_filter = reactive("All")

    def __init__(self, summary_data: dict, all_items: list):
        super().__init__()
        self.top_20 = summary_data.get('top_20', [])
        self.all_items = self._merge_and_normalize(summary_data, all_items)
        self.categories = ["All", "AI/ML", "DevTools", "Security", "Research", "Web", "Other"]
        self.filter_idx = 0

    def _detect_source(self, item: dict) -> str:
        source = item.get('source', '')
        url = item.get('url', '').lower()
        
        if not source or source.lower() == 'unknown':
            if 'arxiv.org' in url: return 'Arxiv'
            if 'github.com' in url: return 'GitHub Trending'
            if 'dev.to' in url: return 'Dev.to'
            if 'ycombinator.com' in url: return 'Hacker News'
            if 'reddit.com' in url: return 'Reddit'
            return source or 'Unknown'
        return source

    def _merge_and_normalize(self, summary_data: dict, all_items: list):
        # First detect sources for all items
        for item in self.top_20:
            item['source'] = self._detect_source(item)
            
        top_urls = {item['url']: item for item in self.top_20}
        merged = list(self.top_20)
        seen_urls = set(top_urls.keys())
        
        for item in all_items:
            if item['url'] not in seen_urls:
                # Basic normalization for raw items
                normalized = {
                    'rank': '-',
                    'title': item.get('title', 'No Title'),
                    'url': item.get('url'),
                    'source': self._detect_source(item),
                    'category': 'Other',
                    'importance': 0,
                    'summary': item.get('summary') or 'No summary available.',
                    'date': item.get('date', datetime.now().strftime('%Y-%m-%d'))
                }
                merged.append(normalized)
                seen_urls.add(item['url'])
        
        # Sort by importance descending
        def sort_key(x):
            try:
                return float(x.get('importance', 0))
            except:
                return 0.0
        
        return sorted(merged, key=sort_key, reverse=True)

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="list-container"):
            yield ListView(id="tech-list")
        with DetailPanel(id="detail-container"):
            yield Static("Select an item from the list")
        yield Footer()

    def on_mount(self):
        self.update_list()

    def update_list(self):
        list_view = self.query_one("#tech-list", ListView)
        list_view.clear()
        
        base_list = self.all_items if self.show_all else self.top_20
        
        filtered = [
            item for item in base_list 
            if self.current_filter == "All" or item.get('category') == self.current_filter
        ]
        
        for item in filtered:
            list_view.append(TechItem(item))
            
        list_view.append(ToggleItem(self.show_all))
        
        # Update header info
        total = len(self.all_items)
        shown = len(filtered)
        self.sub_title = f"Showing {shown} of {total} items | Filter: {self.current_filter} | Mode: {'All' if self.show_all else 'Top 20'}"

    def on_list_view_highlighted(self, event: ListView.Highlighted):
        if event.item and isinstance(event.item, TechItem):
            self.query_one(DetailPanel).update_content(event.item.item)

    def on_list_view_selected(self, event: ListView.Selected):
        if isinstance(event.item, ToggleItem):
            self.action_toggle_mode()
        elif isinstance(event.item, TechItem):
            self.query_one(DetailPanel).focus()

    def action_cycle_filter(self):
        self.filter_idx = (self.filter_idx + 1) % len(self.categories)
        self.current_filter = self.categories[self.filter_idx]
        self.update_list()

    def action_toggle_mode(self):
        self.show_all = not self.show_all
        self.update_list()

    def action_open_url(self):
        list_view = self.query_one("#tech-list", ListView)
        if list_view.index is not None:
            item = list_view.children[list_view.index]
            if isinstance(item, TechItem):
                url = item.item.get('url')
                if url:
                    webbrowser.open(url)

def launch_interactive(summary_data: dict, all_items: list):
    app = TechRadarApp(summary_data, all_items)
    app.run()

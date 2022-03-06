"""Print theme color palette from a VS Code theme file."""

from typing import List, Tuple

import json5
import typer
from PIL import ImageColor
from rich.console import Console
from rich.style import Style
from rich.table import Table, box
from rich.text import Text


def colors(theme_file: str):
    """Print theme color palette from a VS Code theme file."""
    colors = get_colors_from_json_theme(theme_file)

    table = Table(show_header=False, box=box.SQUARE)
    table.add_column("Color")
    table.add_column("Hex")
    table.add_column("RGB")
    rows = [
        (bar(10, color), color, rich_rgb_str(hex_to_rgb(color))) for color in colors
    ]
    rows.sort(key=lambda x: x[2])
    for row in rows:
        table.add_row(*row)
    console = Console()
    console.print(table)


def get_colors_from_json_theme(theme_file: str) -> List[str]:
    with open(theme_file, "r") as f:
        # use json5 to parse the theme file as it supports comments and trailing commas
        # which are prevalent in VS Code theme files
        theme = json5.load(f)

    # colors in the "colors" section then in the "tokenColors" section
    colors = [v for k, v in theme.get("colors", []).items()]
    for token in theme.get("tokenColors", []):
        if "settings" in token:
            try:
                colors.append(token["settings"]["foreground"])
            except KeyError:
                pass
    colors = drop_alpha(colors)
    colors = list(set(colors))
    return colors


def drop_alpha(colors: List[str]) -> List[str]:
    """Remove alpha value from color strings."""
    # drop the alpha channel if present
    new_colors = []
    for color in colors:
        if len(color) == 9:
            # #RRGGBBAA
            color = color[:7]
        elif len(color) == 4:
            # #RGBA
            color = color[:3]
        new_colors.append(color)
    return new_colors


def hex_to_rgb(color: str) -> Tuple[int, int, int]:
    """Get RGB color value from hex color string in format #RGB, #RGBA, #RRGGBB, or #RRGGBBAA"""
    return ImageColor.getrgb(color)


def bar(length: int, color: str) -> str:
    """Create a color bar."""
    bar = "█" * length
    color = hex_to_rgb(color)
    return Text(bar, style=Style(color=rich_rgb_str(color)))


def rich_rgb_str(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to string with RGB values separated by commas."""
    # drop alpha value if present
    return "rgb(" + ",".join(str(c) for c in rgb[:3]) + ")"


def main(theme_file: str = typer.Argument(..., help="Path to VS Code theme file")):
    """Print theme color palette from a VS Code theme file."""
    colors(theme_file)


if __name__ == "__main__":
    typer.run(main)

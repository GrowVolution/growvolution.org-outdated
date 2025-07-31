from shared.packaging import Package

from pathlib import Path

DATABASE = Package(
    Path(__file__).parent,
    lambda *a: lambda cls: cls
)

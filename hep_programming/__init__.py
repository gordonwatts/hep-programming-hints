"""
HEP Programming Hints - MCP Server for High Energy Physics Programming

This package provides an MCP (Model Context Protocol) server that exposes
programming hints and guidance for HEP analysis using IRIS-HEP tools.
"""

__version__ = "0.1.0"

from .server import app

__all__ = ["app"]

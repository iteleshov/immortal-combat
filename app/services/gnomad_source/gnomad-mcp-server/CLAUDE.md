# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a gnomAD MCP (Model Context Protocol) server that provides access to the Genome Aggregation Database through the MCP protocol. The server allows LLMs and other tools to query genomic variant data from gnomAD.

## Development Commands

Note: This appears to be a new repository. Common commands will be added as the project develops.

## Architecture

This MCP server will likely follow the standard MCP server pattern:
- Server implementation handling MCP protocol messages
- Resource providers for gnomAD data access
- Tool handlers for genomic queries
- Configuration for database connections and API endpoints

## Key Considerations

- Handle genomic coordinates and variant identifiers carefully
- Ensure proper error handling for invalid genomic queries
- Consider rate limiting and caching for gnomAD API calls
- Follow genomic data standards (VCF, HGVS notation, etc.)
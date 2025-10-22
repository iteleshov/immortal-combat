FORK FROM https://github.com/shukwong/gnomad-mcp-server

# gnomAD MCP Server

A Model Context Protocol (MCP) server that provides access to the gnomAD (Genome Aggregation Database) GraphQL API. This server enables AI assistants to query genetic variant data, gene constraints, and population genetics information from gnomAD.

## Features

- 🧬 **Gene Information**: Search and retrieve detailed gene data including constraint scores
- 🔬 **Variant Analysis**: Query specific variants and their population frequencies
- 📊 **Population Genetics**: Access allele frequencies across different populations
- 🧮 **Constraint Scores**: Get pLI, LOEUF, and other constraint metrics
- 🔍 **Region Queries**: Find variants within specific genomic regions
- 🧪 **Transcript Data**: Access transcript-specific information and constraints
- 📈 **Coverage Data**: Retrieve sequencing coverage statistics
- 🔄 **Structural Variants**: Query structural variant data
- 🧲 **Mitochondrial Variants**: Access mitochondrial genome variants

## Installation

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Install from source

```bash
git clone https://github.com/yourusername/gnomad-mcp-server.git
cd gnomad-mcp-server
npm install
npm run build
```

## Configuration

### Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gnomad": {
      "command": "node",
      "args": ["/path/to/gnomad-mcp-server/dist/index.js"]
    }
  }
}
```

### With MCP CLI

```bash
npx @modelcontextprotocol/cli gnomad-mcp-server
```

## Available Tools

### 1. `search`
Search for genes, variants, or regions in gnomAD.

**Parameters:**
- `query` (required): Search query (gene symbol, gene ID, variant ID, rsID)
- `reference_genome`: Reference genome (GRCh37 or GRCh38, default: GRCh38)
- `dataset`: Dataset ID (gnomad_r4, gnomad_r3, gnomad_r2_1, etc., default: gnomad_r4)

**Example:**
```json
{
  "query": "TP53",
  "reference_genome": "GRCh38"
}
```

### 2. `get_gene`
Get detailed information about a gene including constraint scores.

**Parameters:**
- `gene_id`: Ensembl gene ID (e.g., ENSG00000141510)
- `gene_symbol`: Gene symbol (e.g., TP53)
- `reference_genome`: Reference genome (default: GRCh38)

**Example:**
```json
{
  "gene_symbol": "BRCA1",
  "reference_genome": "GRCh38"
}
```

### 3. `get_variant`
Get detailed information about a specific variant.

**Parameters:**
- `variant_id` (required): Variant ID in format: chr-pos-ref-alt (e
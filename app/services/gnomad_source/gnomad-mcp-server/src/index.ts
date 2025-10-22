import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import fetch, { Response } from "node-fetch";

// gnomAD GraphQL API endpoint
const GNOMAD_API_URL = "https://gnomad.broadinstitute.org/api";

// Type definitions for gnomAD responses
interface GnomadResponse {
  data?: any;
  errors?: Array<{
    message: string;
    extensions?: any;
  }>;
}

interface GeneConstraint {
  exp_lof: number;
  exp_mis: number;
  exp_syn: number;
  obs_lof: number;
  obs_mis: number;
  obs_syn: number;
  oe_lof: number;
  oe_lof_lower: number;
  oe_lof_upper: number;
  oe_mis: number;
  oe_mis_lower: number;
  oe_mis_upper: number;
  oe_syn: number;
  oe_syn_lower: number;
  oe_syn_upper: number;
  lof_z: number;
  mis_z: number;
  syn_z: number;
  pLI: number;
}

// Helper function to make GraphQL requests
async function makeGraphQLRequest(query: string, variables: Record<string, any> = {}): Promise<GnomadResponse> {
  const response: Response = await fetch(GNOMAD_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query,
      variables,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json() as GnomadResponse;
}

// GraphQL query templates
const QUERIES = {
  searchGene: `
    query SearchGene($query: String!, $referenceGenome: ReferenceGenomeId!) {
      searchResults(query: $query, referenceGenome: $referenceGenome) {
        label
        value: url
      }
    }
  `,

  getGene: `
    query GetGene($geneId: String, $geneSymbol: String, $referenceGenome: ReferenceGenomeId!) {
      gene(gene_id: $geneId, gene_symbol: $geneSymbol, reference_genome: $referenceGenome) {
        gene_id
        symbol
        name
        canonical_transcript_id
        hgnc_id
        omim_id
        chrom
        start
        stop
        strand
        gnomad_constraint {
          exp_lof
          exp_mis
          exp_syn
          obs_lof
          obs_mis
          obs_syn
          oe_lof
          oe_lof_lower
          oe_lof_upper
          oe_mis
          oe_mis_lower
          oe_mis_upper
          oe_syn
          oe_syn_lower
          oe_syn_upper
          lof_z
          mis_z
          syn_z
          pLI
        }
        transcripts {
          transcript_id
          transcript_version
          reference_genome
        }
      }
    }
  `,

  getVariant: `
    query GetVariant($variantId: String!, $datasetId: DatasetId!) {
      variant(variantId: $variantId, dataset: $datasetId) {
        variant_id
        reference_genome
        chrom
        pos
        ref
        alt
        rsids
        caid
        colocated_variants
        multi_nucleotide_variants {
          combined_variant_id
          changes_amino_acids
          n_individuals
          other_constituent_snvs
        }
        exome {
          ac
          an
          ac_hemi
          ac_hom
          faf95 {
            popmax
            popmax_population
          }
          filters
          populations {
            id
            ac
            an
            ac_hemi
            ac_hom
          }
        }
        genome {
          ac
          an
          ac_hemi
          ac_hom
          faf95 {
            popmax
            popmax_population
          }
          filters
          populations {
            id
            ac
            an
            ac_hemi
            ac_hom
          }
        }
        transcript_consequences {
          gene_id
          gene_symbol
          transcript_id
          consequence_terms
          is_canonical
          major_consequence
          polyphen_prediction
          sift_prediction
          lof
          lof_filter
          lof_flags
        }
      }
    }
  `,

  getClinVarVariantsInGene: `
    query GetVariantsInGene($geneId: String, $referenceGenome: ReferenceGenomeId!) {
      gene(gene_id: $geneId, reference_genome: $referenceGenome) {
        clinvar_variants {
          clinical_significance
          clinvar_variation_id
          gnomad {
            exome {
              ac
              an
              filters
            }
            genome {
              ac
              an
              filters
            }
          }
          gold_stars
          hgvsc
          hgvsp
          in_gnomad
          major_consequence
          pos
          review_status
          transcript_id
          variant_id
        }
      } 
    }
  `, 

  getVariantsInGene: `
    query GetVariantsInGene($geneId: String, $geneSymbol: String, $datasetId: DatasetId!, $referenceGenome: ReferenceGenomeId!) {
      gene(gene_id: $geneId, gene_symbol: $geneSymbol, reference_genome: $referenceGenome) {
        variants(dataset: $datasetId) {
          variant_id
          pos
          rsids
          consequence
          hgvsc
          hgvsp
          lof
          exome {
            ac
            an
            af
            filters
          }
          genome {
            ac
            an
            af
            filters
          }
        }
      }
    }
  `,

  getTranscript: `
    query GetTranscript($transcriptId: String!, $referenceGenome: ReferenceGenomeId!) {
      transcript(transcript_id: $transcriptId, reference_genome: $referenceGenome) {
        transcript_id
        transcript_version
        reference_genome
        chrom
        start
        stop
        strand
        gene_id
        gene_symbol
        gene_version
        gnomad_constraint {
          exp_lof
          exp_mis
          exp_syn
          obs_lof
          obs_mis
          obs_syn
          oe_lof
          oe_lof_lower
          oe_lof_upper
          oe_mis
          oe_mis_lower
          oe_mis_upper
          oe_syn
          oe_syn_lower
          oe_syn_upper
          lof_z
          mis_z
          syn_z
          pLI
        }
      }
    }
  `,

  getRegionVariants: `
    query GetRegionVariants($chrom: String!, $start: Int!, $stop: Int!, $datasetId: DatasetId!, $referenceGenome: ReferenceGenomeId!) {
      region(chrom: $chrom, start: $start, stop: $stop, reference_genome: $referenceGenome) {
        variants(dataset: $datasetId) {
          variant_id
          pos
          rsids
          consequence
          hgvsc
          hgvsp
          lof
          exome {
            ac
            an
            af
            filters
          }
          genome {
            ac
            an
            af
            filters
          }
        }
      }
    }
  `,

  getCoverage: `
    query GetCoverage($geneId: String, $geneSymbol: String, $datasetId: DatasetId!, $referenceGenome: ReferenceGenomeId!) {
      gene(gene_id: $geneId, gene_symbol: $geneSymbol, reference_genome: $referenceGenome) {
        coverage(dataset: $datasetId) {
          exome {
            pos
            mean
            median
            over_1
            over_5
            over_10
            over_15
            over_20
            over_25
            over_30
            over_50
            over_100
          }
          genome {
            pos
            mean
            median
            over_1
            over_5
            over_10
            over_15
            over_20
            over_25
            over_30
            over_50
            over_100
          }
        }
      }
    }
  `,

  getStructuralVariants: `
    query GetStructuralVariants($chrom: String!, $start: Int!, $stop: Int!, $datasetId: DatasetId!, $referenceGenome: ReferenceGenomeId!) {
      region(chrom: $chrom, start: $start, stop: $stop, reference_genome: $referenceGenome) {
        structural_variants(dataset: $datasetId) {
          variant_id
          chrom
          pos
          end
          length
          type
          alts
          ac
          an
          af
          homozygote_count
          hemizygote_count
          filters
        }
      }
    }
  `,

  getMitochondrialVariants: `
    query GetMitochondrialVariants($datasetId: DatasetId!) {
      mitochondrial_variants(dataset: $datasetId) {
        variant_id
        pos
        ref
        alt
        rsids
        ac_het
        ac_hom
        an
        af_het
        af_hom
        max_heteroplasmy
        filters
      }
    }
  `,

  searchVariant: `
    query SearchVariant($query: String!, $datasetId: DatasetId!, $referenceGenome: ReferenceGenomeId!) {
      searchResults(query: $query, referenceGenome: $referenceGenome, dataset: $datasetId) {
        label
        value: url
      }
    }
  `
};

// Create the MCP server
const server = new Server(
  {
    name: "gnomad-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Helper function to validate and parse dataset ID
function parseDatasetId(dataset: string): string {
  const validDatasets = [
    "gnomad_r2_1",
    "gnomad_r3",
    "gnomad_r4",
    "gnomad_sv_r2_1",
    "gnomad_sv_r4",
    "gnomad_cnv_r4",
    "exac",
  ];
  
  const datasetLower = dataset.toLowerCase();
  if (!validDatasets.includes(datasetLower)) {
    return "gnomad_r4"; // Default to latest version
  }
  return datasetLower;
}

// Helper function to validate reference genome
function parseReferenceGenome(genome: string): string {
  const validGenomes = ["GRCh37", "GRCh38"];
  if (!validGenomes.includes(genome)) {
    return "GRCh38"; // Default to GRCh38
  }
  return genome;
}

// Register tool handlers
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "search",
        description: "Search for genes, variants, or regions in gnomAD",
        inputSchema: {
          type: "object",
          properties: {
            query: {
              type: "string",
              description: "Search query (gene symbol, gene ID, variant ID, rsID, etc.)",
            },
            reference_genome: {
              type: "string",
              description: "Reference genome (GRCh37 or GRCh38)",
              default: "GRCh38",
            },
            dataset: {
              type: "string",
              description: "Dataset ID (gnomad_r4, gnomad_r3, gnomad_r2_1, etc.)",
              default: "gnomad_r4",
            },
          },
          required: ["query"],
        },
      },
      {
        name: "get_gene",
        description: "Get detailed information about a gene including constraint scores",
        inputSchema: {
          type: "object",
          properties: {
            gene_id: {
              type: "string",
              description: "Ensembl gene ID (e.g., ENSG00000141510)",
            },
            gene_symbol: {
              type: "string",
              description: "Gene symbol (e.g., TP53)",
            },
            reference_genome: {
              type: "string",
              description: "Reference genome (GRCh37 or GRCh38)",
              default: "GRCh38",
            },
          },
        },
      },
      {
        name: "get_variant",
        description: "Get detailed information about a specific variant",
        inputSchema: {
          type: "object",
          properties: {
            variant_id: {
              type: "string",
              description: "Variant ID in format: chr-pos-ref-alt (e.g., 1-55516888-G-A)",
            },
            dataset: {
              type: "string",
              description: "Dataset ID (gnomad_r4, gnomad_r3, gnomad_r2_1, etc.)",
              default: "gnomad_r4",
            },
          },
          required: ["variant_id"],
        },
      },
      {
        name: "get_clinvar_variants_in_gene",
        description: "Get all ClinVar variants in a specific gene",
        inputSchema: {
          type: "object",
          properties: {
            gene_id: {
              type: "string",
              description: "Ensembl gene ID",
            },
             reference_genome: {
              type: "string",
              description: "Reference genome",
              default: "GRCh38",
            },
          },
          required: ["gene_id"],
        }
      },
      {
        name: "get_variants_in_gene",
        description: "Get all variants in a specific gene",
        inputSchema: {
          type: "object",
          properties: {
            gene_id: {
              type: "string",
              description: "Ensembl gene ID",
            },
            gene_symbol: {
              type: "string",
              description: "Gene symbol",
            },
            dataset: {
              type: "string",
              description: "Dataset ID",
              default: "gnomad_r4",
            },
            reference_genome: {
              type: "string",
              description: "Reference genome",
              default: "GRCh38",
            },
          },
        },
      },
      {
        name: "get_transcript",
        description: "Get information about a specific transcript",
        inputSchema: {
          type: "object",
          properties: {
            transcript_id: {
              type: "string",
              description: "Ensembl transcript ID (e.g., ENST00000269305)",
            },
            reference_genome: {
              type: "string",
              description: "Reference genome",
              default: "GRCh38",
            },
          },
          required: ["transcript_id"],
        },
      },
      {
        name: "get_region_variants",
        description: "Get variants in a specific genomic region",
        inputSchema: {
          type: "object",
          properties: {
            chrom: {
              type: "string",
              description: "Chromosome (1-22, X, Y)",
            },
            start: {
              type: "number",
              description: "Start position",
            },
            stop: {
              type: "number",
              description: "Stop position",
            },
            dataset: {
              type: "string",
              description: "Dataset ID",
              default: "gnomad_r4",
            },
            reference_genome: {
              type: "string",
              description: "Reference genome",
              default: "GRCh38",
            },
          },
          required: ["chrom", "start", "stop"],
        },
      },
      {
        name: "get_coverage",
        description: "Get coverage information for a gene",
        inputSchema: {
          type: "object",
          properties: {
            gene_id: {
              type: "string",
              description: "Ensembl gene ID",
            },
            gene_symbol: {
              type: "string",
              description: "Gene symbol",
            },
            dataset: {
              type: "string",
              description: "Dataset ID",
              default: "gnomad_r4",
            },
            reference_genome: {
              type: "string",
              description: "Reference genome",
              default: "GRCh38",
            },
          },
        },
      },
      {
        name: "get_structural_variants",
        description: "Get structural variants in a genomic region",
        inputSchema: {
          type: "object",
          properties: {
            chrom: {
              type: "string",
              description: "Chromosome",
            },
            start: {
              type: "number",
              description: "Start position",
            },
            stop: {
              type: "number",
              description: "Stop position",
            },
            dataset: {
              type: "string",
              description: "Dataset ID (gnomad_sv_r4, gnomad_sv_r2_1)",
              default: "gnomad_sv_r4",
            },
            reference_genome: {
              type: "string",
              description: "Reference genome",
              default: "GRCh38",
            },
          },
          required: ["chrom", "start", "stop"],
        },
      },
      {
        name: "get_mitochondrial_variants",
        description: "Get mitochondrial variants",
        inputSchema: {
          type: "object",
          properties: {
            dataset: {
              type: "string",
              description: "Dataset ID",
              default: "gnomad_r3",
            },
          },
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  // Type guard for arguments
  if (!args || typeof args !== 'object') {
    throw new Error("Invalid arguments provided");
  }

  try {
    let result: GnomadResponse;
    let formattedResult: any;

    switch (name) {
      case "search":
        result = await makeGraphQLRequest(QUERIES.searchGene, {
          query: args.query as string,
          referenceGenome: parseReferenceGenome((args.reference_genome as string) || "GRCh38"),
        });
        formattedResult = result.data?.searchResults || [];
        break;

      case "get_gene":
        if (!args.gene_id && !args.gene_symbol) {
          throw new Error("Either gene_id or gene_symbol must be provided");
        }
        result = await makeGraphQLRequest(QUERIES.getGene, {
          geneId: (args.gene_id as string) || null,
          geneSymbol: (args.gene_symbol as string) || null,
          referenceGenome: parseReferenceGenome((args.reference_genome as string) || "GRCh38"),
        });
        formattedResult = result.data?.gene || null;
        break;

      case "get_variant":
        result = await makeGraphQLRequest(QUERIES.getVariant, {
          variantId: args.variant_id as string,
          datasetId: parseDatasetId((args.dataset as string) || "gnomad_r4"),
        });
        formattedResult = result.data?.variant || null;
        break;

      case "get_clinvar_variants_in_gene":
        if (!args.gene_id) {
          throw new Error("Gene_id must be provided");
        }
        result = await makeGraphQLRequest(QUERIES.getClinVarVariantsInGene, {
          geneId: (args.gene_id as string) || null,
          referenceGenome: parseReferenceGenome((args.reference_genome as string) || "GRCh38"),
        });
        formattedResult = result.data?.gene?.clinvar_variants || [];
        break;

      case "get_variants_in_gene":
        if (!args.gene_id && !args.gene_symbol) {
          throw new Error("Either gene_id or gene_symbol must be provided");
        }
        result = await makeGraphQLRequest(QUERIES.getVariantsInGene, {
          geneId: (args.gene_id as string) || null,
          geneSymbol: (args.gene_symbol as string) || null,
          datasetId: parseDatasetId((args.dataset as string) || "gnomad_r4"),
          referenceGenome: parseReferenceGenome((args.reference_genome as string) || "GRCh38"),
        });
        formattedResult = result.data?.gene?.variants || [];
        break;

      case "get_transcript":
        result = await makeGraphQLRequest(QUERIES.getTranscript, {
          transcriptId: args.transcript_id as string,
          referenceGenome: parseReferenceGenome((args.reference_genome as string) || "GRCh38"),
        });
        formattedResult = result.data?.transcript || null;
        break;

      case "get_region_variants":
        result = await makeGraphQLRequest(QUERIES.getRegionVariants, {
          chrom: String(args.chrom),
          start: parseInt(String(args.start)),
          stop: parseInt(String(args.stop)),
          datasetId: parseDatasetId((args.dataset as string) || "gnomad_r4"),
          referenceGenome: parseReferenceGenome((args.reference_genome as string) || "GRCh38"),
        });
        formattedResult = result.data?.region?.variants || [];
        break;

      case "get_coverage":
        if (!args.gene_id && !args.gene_symbol) {
          throw new Error("Either gene_id or gene_symbol must be provided");
        }
        result = await makeGraphQLRequest(QUERIES.getCoverage, {
          geneId: (args.gene_id as string) || null,
          geneSymbol: (args.gene_symbol as string) || null,
          datasetId: parseDatasetId((args.dataset as string) || "gnomad_r4"),
          referenceGenome: parseReferenceGenome((args.reference_genome as string) || "GRCh38"),
        });
        formattedResult = result.data?.gene?.coverage || null;
        break;

      case "get_structural_variants":
        result = await makeGraphQLRequest(QUERIES.getStructuralVariants, {
          chrom: String(args.chrom),
          start: parseInt(String(args.start)),
          stop: parseInt(String(args.stop)),
          datasetId: parseDatasetId((args.dataset as string) || "gnomad_sv_r4"),
          referenceGenome: parseReferenceGenome((args.reference_genome as string) || "GRCh38"),
        });
        formattedResult = result.data?.region?.structural_variants || [];
        break;

      case "get_mitochondrial_variants":
        result = await makeGraphQLRequest(QUERIES.getMitochondrialVariants, {
          datasetId: parseDatasetId((args.dataset as string) || "gnomad_r3"),
        });
        formattedResult = result.data?.mitochondrial_variants || [];
        break;

      default:
        throw new Error(`Unknown tool: ${name}`);
    }

    // Check for GraphQL errors
    if (result.errors && result.errors.length > 0) {
      const errorMessages = result.errors.map(e => e.message).join("; ");
      throw new Error(`GraphQL errors: ${errorMessages}`);
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(formattedResult, null, 2),
        },
      ],
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return {
      content: [
        {
          type: "text",
          text: `Error: ${errorMessage}`,
        },
      ],
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("gnomAD MCP server started");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
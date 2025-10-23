"""NCBI E-utilities and BLAST client for MCP server."""

import asyncio
import os
import tempfile
import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

import httpx
import xmltodict
from Bio import SeqIO
from Bio.Blast import NCBIWWW, NCBIXML
from pydantic import BaseModel


class NCBIConfig(BaseModel):
    """Configuration for NCBI client."""

    api_key: Optional[str] = None
    email: Optional[str] = None
    tool: str = "ncbi-mcp-server"
    base_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    blast_base_url: str = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"


class SearchResult(BaseModel):
    """Search result from NCBI."""

    count: int
    retmax: int
    retstart: int
    ids: List[str]
    query_translation: Optional[str] = None
    web_env: Optional[str] = None
    query_key: Optional[str] = None


class SummaryResult(BaseModel):
    """Summary result from NCBI."""

    uid: str
    title: str
    authors: List[str]
    journal: Optional[str] = None
    pub_date: Optional[str] = None
    doi: Optional[str] = None
    pmid: Optional[str] = None
    abstract: Optional[str] = None
    description: Optional[str] = None


class BlastResult(BaseModel):
    """BLAST result from NCBI."""

    rid: str
    status: str
    results: Optional[Dict[str, Any]] = None


class NCBIClient:
    """Client for interacting with NCBI E-utilities and BLAST."""

    def __init__(self, config: NCBIConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _build_base_params(self) -> Dict[str, str]:
        """Build base parameters for E-utilities requests."""
        params = {"tool": self.config.tool, "retmode": "xml"}
        if self.config.api_key:
            params["api_key"] = self.config.api_key
        if self.config.email:
            params["email"] = self.config.email
        return params

    async def _make_request(
            self, endpoint: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make an HTTP request to NCBI E-utilities."""
        url = f"{self.config.base_url}/{endpoint}.fcgi"

        # Add rate limiting if no API key
        if not self.config.api_key:
            await asyncio.sleep(0.34)  # ~3 requests per second
        else:
            await asyncio.sleep(0.1)  # ~10 requests per second with API key

        response = await self.client.get(url, params=params)
        response.raise_for_status()

        # Parse XML response
        return xmltodict.parse(response.text)

    async def search(
            self,
            database: str,
            query: str,
            retmax: int = 20,
            retstart: int = 0,
            sort: Optional[str] = None,
            use_history: bool = False,
    ) -> SearchResult:
        """Search NCBI database using ESearch."""
        params = self._build_base_params()
        params.update(
            {
                "db": database,
                "term": query,
                "retmax": str(retmax),
                "retstart": str(retstart),
            }
        )

        if sort:
            params["sort"] = sort
        if use_history:
            params["usehistory"] = "y"

        result = await self._make_request("esearch", params)

        # Parse the result
        search_result = result["eSearchResult"]
        ids = []
        if "IdList" in search_result and search_result["IdList"]:
            id_list = search_result["IdList"]["Id"]
            if isinstance(id_list, list):
                ids = id_list
            else:
                ids = [id_list]

        return SearchResult(
            count=int(search_result.get("Count", 0)),
            retmax=int(search_result.get("RetMax", 0)),
            retstart=int(search_result.get("RetStart", 0)),
            ids=ids,
            query_translation=search_result.get("QueryTranslation"),
            web_env=search_result.get("WebEnv"),
            query_key=search_result.get("QueryKey"),
        )

    async def fetch(
            self,
            database: str,
            ids: Union[List[str], str],
            rettype: str = "xml",
            retmode: str = "xml",
    ) -> str:
        """Fetch records from NCBI database using EFetch."""
        if isinstance(ids, list):
            id_str = ",".join(ids)
        else:
            id_str = ids

        params = self._build_base_params()
        params.update(
            {"db": database, "id": id_str, "rettype": rettype, "retmode": retmode}
        )

        url = f"{self.config.base_url}/efetch.fcgi"
        response = await self.client.get(url, params=params)
        response.raise_for_status()

        return response.text

    async def summary(
            self, database: str, ids: Union[List[str], str]
    ) -> List[SummaryResult]:
        """Get document summaries using ESummary."""
        if isinstance(ids, list):
            id_str = ",".join(ids)
        else:
            id_str = ids

        params = self._build_base_params()
        params.update({"db": database, "id": id_str})

        result = await self._make_request("esummary", params)

        # Parse the result
        summaries = []
        if "eSummaryResult" in result:
            # ИСПРАВЛЕНИЕ: Разные структуры для разных баз данных
            if database == 'gene':
                # Для gene базы используем DocumentSummarySet
                if "DocumentSummarySet" in result["eSummaryResult"]:
                    doc_sum_set = result["eSummaryResult"]["DocumentSummarySet"]
                    doc_sum_list = doc_sum_set.get("DocumentSummary", [])
                else:
                    doc_sum_list = []
            else:
                # Для других баз используем стандартную структуру DocSum
                doc_sum_list = result["eSummaryResult"].get("DocSum", [])

            if not isinstance(doc_sum_list, list):
                doc_sum_list = [doc_sum_list]

            for doc_sum in doc_sum_list:
                if database == 'gene':
                    # ОСОБАЯ ОБРАБОТКА ДЛЯ GENE БАЗЫ
                    summary = SummaryResult(
                        uid=doc_sum.get("@uid", ""),
                        title=doc_sum.get("Name", "Not available"),  # Используем Name вместо Title
                        authors=[],  # У генов нет авторов
                        journal=None,
                        pub_date=None,
                        doi=None,
                        pmid=None
                    )

                    # Для генов добавляем дополнительные поля в description
                    description_parts = []
                    if doc_sum.get("Description"):
                        description_parts.append(doc_sum["Description"])
                    if doc_sum.get("Summary"):
                        description_parts.append(doc_sum["Summary"])
                    if doc_sum.get("Chromosome"):
                        description_parts.append(f"Chromosome: {doc_sum['Chromosome']}")
                    if doc_sum.get("MapLocation"):
                        description_parts.append(f"Location: {doc_sum['MapLocation']}")

                    if description_parts:
                        summary.description = " | ".join(description_parts)

                else:
                    # СТАНДАРТНАЯ ОБРАБОТКА ДЛЯ ДРУГИХ БАЗ (protein, pubmed, etc.)
                    summary = SummaryResult(
                        uid=doc_sum.get("Id", ""),
                        title="",
                        authors=[]
                    )

                    # Extract fields from Items (для protein/pubmed)
                    if "Item" in doc_sum:
                        items = doc_sum["Item"]
                        if not isinstance(items, list):
                            items = [items]

                        for item in items:
                            name = item.get("@Name", "")
                            value = item.get("#text", "")

                            if name == "Title":
                                summary.title = value
                            elif name == "AuthorList":
                                if isinstance(value, str):
                                    summary.authors = [value]
                                elif isinstance(value, list):
                                    summary.authors = value
                            elif name == "FullJournalName":
                                summary.journal = value
                            elif name == "PubDate":
                                summary.pub_date = value
                            elif name == "DOI":
                                summary.doi = value
                            elif name == "PMID":
                                summary.pmid = value

                summaries.append(summary)

        return summaries

    async def link(
            self, database_from: str, database_to: str, ids: Union[List[str], str]
    ) -> List[str]:
        """Find related records using ELink."""
        if isinstance(ids, list):
            id_str = ",".join(ids)
        else:
            id_str = ids

        params = self._build_base_params()
        params.update({"dbfrom": database_from, "db": database_to, "id": id_str})

        result = await self._make_request("elink", params)

        # Parse the result
        linked_ids = []
        if "eLinkResult" in result and "LinkSet" in result["eLinkResult"]:
            link_set = result["eLinkResult"]["LinkSet"]
            if not isinstance(link_set, list):
                link_set = [link_set]

            for ls in link_set:
                if "LinkSetDb" in ls:
                    link_set_db = ls["LinkSetDb"]
                    if not isinstance(link_set_db, list):
                        link_set_db = [link_set_db]

                    for lsdb in link_set_db:
                        if "Link" in lsdb:
                            links = lsdb["Link"]
                            if not isinstance(links, list):
                                links = [links]

                            for link in links:
                                if "Id" in link:
                                    linked_ids.append(link["Id"])

        return linked_ids

    async def info(self, database: Optional[str] = None) -> Dict[str, Any]:
        """Get information about NCBI databases using EInfo."""
        params = self._build_base_params()
        if database:
            params["db"] = database

        result = await self._make_request("einfo", params)
        return result

    async def blast_search(
            self,
            program: str,
            database: str,
            sequence: str,
            expect: float = 10.0,
            word_size: Optional[int] = None,
            matrix: Optional[str] = None,
            gapcosts: Optional[str] = None,
    ) -> BlastResult:
        """Submit a BLAST search."""
        # Use Biopython's BLAST interface
        try:
            # Submit BLAST job
            result_handle = NCBIWWW.qblast(
                program=program,
                database=database,
                sequence=sequence,
                expect=expect,
                word_size=word_size,
                matrix_name=matrix,
                gapcosts=gapcosts,
            )

            # Parse results
            blast_records = NCBIXML.parse(result_handle)
            records = list(blast_records)

            # Convert to serializable format
            results = []
            for record in records:
                record_data = {
                    "query": record.query,
                    "query_length": record.query_length,
                    "alignments": [],
                }

                for alignment in record.alignments:
                    alignment_data = {
                        "title": alignment.title,
                        "length": alignment.length,
                        "hsps": [],
                    }

                    for hsp in alignment.hsps:
                        hsp_data = {
                            "score": hsp.score,
                            "bits": hsp.bits,
                            "expect": hsp.expect,
                            "query_start": hsp.query_start,
                            "query_end": hsp.query_end,
                            "sbjct_start": hsp.sbjct_start,
                            "sbjct_end": hsp.sbjct_end,
                            "query": hsp.query,
                            "match": hsp.match,
                            "sbjct": hsp.sbjct,
                        }
                        alignment_data["hsps"].append(hsp_data)

                    record_data["alignments"].append(alignment_data)

                results.append(record_data)

            return BlastResult(
                rid="completed", status="completed", results={"records": results}
            )

        except Exception as e:
            return BlastResult(rid="error", status="error", results={"error": str(e)})

    async def get_databases(self) -> List[str]:
        """Get list of available NCBI databases."""
        try:
            info_result = await self.info()
            databases = []

            if "eInfoResult" in info_result and "DbList" in info_result["eInfoResult"]:
                db_list = info_result["eInfoResult"]["DbList"]["DbName"]
                if isinstance(db_list, list):
                    databases = db_list
                else:
                    databases = [db_list]

            return databases
        except Exception:
            # Return common databases if info fails
            return [
                "pubmed",
                "protein",
                "nucleotide",
                "nuccore",
                "nucest",
                "nucgss",
                "genome",
                "assembly",
                "bioproject",
                "biosample",
                "books",
                "cdd",
                "clinvar",
                "gap",
                "gapplus",
                "grasp",
                "dbvar",
                "gene",
                "gds",
                "geoprofiles",
                "homologene",
                "mesh",
                "nlmcatalog",
                "omim",
                "pmc",
                "popset",
                "probe",
                "proteinclusters",
                "pcassay",
                "pccompound",
                "pcsubstance",
                "snp",
                "sra",
                "taxonomy",
                "unigene",
            ]

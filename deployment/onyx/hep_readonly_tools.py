#!/usr/bin/env python3
"""Install AiSci HEP read-only Onyx tools and seed selected HEP sources.

Run this inside the Onyx API container. It intentionally avoids credentials and
uses public, read-only endpoints only.
"""

from __future__ import annotations

import argparse
import html
import json
import textwrap
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import Any
from urllib.parse import quote

import requests
from sqlalchemy import select

from onyx.configs.constants import DocumentSource
from onyx.connectors.models import DocumentBase
from onyx.connectors.models import InputType
from onyx.connectors.models import TextSection
from onyx.db.engine.sql_engine import SqlEngine
from onyx.db.engine.sql_engine import get_session_with_tenant
from onyx.db.enums import AccessType
from onyx.db.enums import ConnectorCredentialPairStatus
from onyx.db.enums import ProcessingMode
from onyx.db.models import Connector
from onyx.db.models import ConnectorCredentialPair
from onyx.db.models import Credential
from onyx.db.models import DocumentSet
from onyx.db.models import DocumentSet__ConnectorCredentialPair
from onyx.db.models import Persona
from onyx.db.models import Persona__Tool
from onyx.db.models import Tool
from onyx.server.onyx_api.ingestion import IngestionDocument
from onyx.server.onyx_api.ingestion import upsert_ingestion_doc
from onyx.tools.tool_implementations.custom.openapi_parsing import (
    openapi_to_method_specs,
)
from onyx.tools.tool_implementations.custom.openapi_parsing import openapi_to_url
from onyx.tools.tool_implementations.custom.openapi_parsing import (
    validate_openapi_schema,
)
from shared_configs.configs import POSTGRES_DEFAULT_SCHEMA_STANDARD_VALUE
from shared_configs.contextvars import CURRENT_TENANT_ID_CONTEXTVAR


USER_AGENT = "aisci-hep-readonly-tools/0.1"
PHYSICS_PERSONA_NAME = "Physics Validation Mode"
HEP_DOCUMENT_SET_NAME = "HEP Phenomenology References"
HEP_INGESTION_CONNECTOR_NAME = "HEP Native API Sources"


@dataclass(frozen=True)
class ToolSpec:
    name: str
    display_name: str
    description: str
    schema: dict[str, Any]
    test_operation: str
    test_kwargs: dict[str, str | int]


def _json_parameter(
    name: str,
    description: str,
    required: bool = False,
    type_: str = "string",
    default: str | int | None = None,
) -> dict[str, Any]:
    schema: dict[str, Any] = {"type": type_}
    if default is not None:
        schema["default"] = default
    return {
        "name": name,
        "in": "query",
        "required": required,
        "description": description,
        "schema": schema,
    }


def arxiv_schema() -> dict[str, Any]:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "arXiv Atom API",
            "version": "1.0.0",
            "description": "Read-only arXiv lookup for HEP source grounding.",
        },
        "servers": [{"url": "https://export.arxiv.org"}],
        "paths": {
            "/api/query": {
                "get": {
                    "operationId": "hep_arxiv_query",
                    "summary": (
                        "Query arXiv by id_list or search_query. Prefer id_list "
                        "for known arXiv IDs such as 1602.01633."
                    ),
                    "parameters": [
                        _json_parameter(
                            "id_list",
                            "Comma-separated arXiv IDs, for example 1602.01633.",
                        ),
                        _json_parameter(
                            "search_query",
                            "arXiv query string, for example all:ATLAS.",
                        ),
                        _json_parameter(
                            "start",
                            "Zero-based result offset.",
                            type_="integer",
                            default=0,
                        ),
                        _json_parameter(
                            "max_results",
                            "Maximum number of returned records.",
                            type_="integer",
                            default=3,
                        ),
                    ],
                    "responses": {
                        "200": {
                            "description": "arXiv Atom XML feed.",
                            "content": {"application/atom+xml": {"schema": {"type": "string"}}},
                        }
                    },
                }
            }
        },
    }


def inspire_schema() -> dict[str, Any]:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "INSPIRE-HEP Literature API",
            "version": "1.0.0",
            "description": "Read-only INSPIRE-HEP literature lookup.",
        },
        "servers": [{"url": "https://inspirehep.net"}],
        "paths": {
            "/api/literature": {
                "get": {
                    "operationId": "hep_inspire_literature_search",
                    "summary": (
                        "Search INSPIRE-HEP literature records. Use q values such "
                        "as arxiv:1602.01633 or collaboration:ATLAS."
                    ),
                    "parameters": [
                        _json_parameter("q", "INSPIRE search query.", required=True),
                        _json_parameter(
                            "size",
                            "Maximum number of records to return.",
                            type_="integer",
                            default=3,
                        ),
                        _json_parameter("sort", "Optional INSPIRE sort value."),
                        _json_parameter(
                            "page",
                            "Optional one-based page number.",
                            type_="integer",
                        ),
                    ],
                    "responses": {
                        "200": {
                            "description": "INSPIRE literature search JSON.",
                            "content": {"application/json": {"schema": {"type": "object"}}},
                        }
                    },
                }
            },
            "/api/literature/{record_id}": {
                "get": {
                    "operationId": "hep_inspire_literature_record",
                    "summary": "Fetch one INSPIRE-HEP literature record by control number.",
                    "parameters": [
                        {
                            "name": "record_id",
                            "in": "path",
                            "required": True,
                            "description": "INSPIRE control number, for example 1419652.",
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "INSPIRE literature record JSON.",
                            "content": {"application/json": {"schema": {"type": "object"}}},
                        }
                    },
                }
            },
        },
    }


def hepdata_schema() -> dict[str, Any]:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "HEPData Public API",
            "version": "1.0.0",
            "description": "Read-only HEPData record and table lookup.",
        },
        "servers": [{"url": "https://www.hepdata.net"}],
        "paths": {
            "/search/": {
                "get": {
                    "operationId": "hepdata_search",
                    "summary": (
                        "Search HEPData. Always pass format=json for machine-readable output."
                    ),
                    "parameters": [
                        _json_parameter("q", "HEPData free-text query.", required=True),
                        _json_parameter(
                            "format",
                            "Response format. Use json.",
                            default="json",
                        ),
                        _json_parameter(
                            "size",
                            "Maximum number of records to return.",
                            type_="integer",
                            default=3,
                        ),
                    ],
                    "responses": {
                        "200": {
                            "description": "HEPData search JSON.",
                            "content": {"application/json": {"schema": {"type": "object"}}},
                        }
                    },
                }
            },
            "/record/{record_id}?format=json": {
                "get": {
                    "operationId": "hepdata_record_json",
                    "summary": (
                        "Fetch a HEPData record as JSON. record_id can be ins1419652 "
                        "or the HEPData record number."
                    ),
                    "parameters": [
                        {
                            "name": "record_id",
                            "in": "path",
                            "required": True,
                            "description": "HEPData record identifier, for example ins1419652.",
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "HEPData record JSON.",
                            "content": {"application/json": {"schema": {"type": "object"}}},
                        }
                    },
                }
            },
            "/download/table/{inspire_id}/{table_name}/json": {
                "get": {
                    "operationId": "hepdata_table_json",
                    "summary": (
                        "Fetch one HEPData table as JSON. Use inspire_id such as "
                        "ins1419652 and table_name such as Table 4."
                    ),
                    "parameters": [
                        {
                            "name": "inspire_id",
                            "in": "path",
                            "required": True,
                            "description": "INSPIRE-style HEPData record ID, for example ins1419652.",
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "table_name",
                            "in": "path",
                            "required": True,
                            "description": "HEPData table name, for example Table 4.",
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "HEPData table JSON.",
                            "content": {"application/json": {"schema": {"type": "object"}}},
                        }
                    },
                }
            },
        },
    }


TOOL_SPECS = [
    ToolSpec(
        name="hep_arxiv",
        display_name="HEP arXiv Lookup",
        description="Read-only arXiv Atom API lookup for HEP identifiers and PDFs.",
        schema=arxiv_schema(),
        test_operation="hep_arxiv_query",
        test_kwargs={"id_list": "1602.01633", "max_results": 1},
    ),
    ToolSpec(
        name="hep_inspire",
        display_name="INSPIRE-HEP Lookup",
        description="Read-only INSPIRE-HEP literature lookup for canonical HEP records.",
        schema=inspire_schema(),
        test_operation="hep_inspire_literature_search",
        test_kwargs={"q": "arxiv:1602.01633", "size": 1},
    ),
    ToolSpec(
        name="hepdata",
        display_name="HEPData Lookup",
        description="Read-only HEPData record and table lookup for spectra and uncertainties.",
        schema=hepdata_schema(),
        test_operation="hepdata_record_json",
        test_kwargs={"record_id": "ins1419652"},
    ),
]


def _request_json(url: str) -> dict[str, Any]:
    for _ in range(3):
        time.sleep(10)
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=45)
        if response.status_code == 429:
            time.sleep(30)
            continue
        response.raise_for_status()
        return json.loads(response.text, parse_constant=lambda value: value)
    raise RuntimeError(f"Max retries exceeded for {url}")


def _request_text(url: str) -> str:
    for _ in range(3):
        time.sleep(10)
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=45)
        if response.status_code == 429:
            time.sleep(30)
            continue
        response.raise_for_status()
        return response.text
    raise RuntimeError(f"Max retries exceeded for {url}")


def _clean_text(value: Any) -> str:
    return " ".join(html.unescape(str(value or "")).split())


def _hepdata_table_url(table_name: str) -> str:
    return f"https://www.hepdata.net/download/table/ins1419652/{quote(table_name)}/json"


def _arxiv_metadata(arxiv_id: str) -> dict[str, Any]:
    text = _request_text(
        f"https://export.arxiv.org/api/query?id_list={arxiv_id}&max_results=1"
    )
    root = ET.fromstring(text)
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    entry = root.find("atom:entry", ns)
    if entry is None:
        raise RuntimeError(f"arXiv record not found: {arxiv_id}")

    def find_text(path: str) -> str:
        node = entry.find(path, ns)
        return " ".join((node.text or "").split()) if node is not None else ""

    links = [
        {key: value for key, value in link.attrib.items()}
        for link in entry.findall("atom:link", ns)
    ]
    return {
        "id": find_text("atom:id"),
        "title": find_text("atom:title"),
        "summary": find_text("atom:summary"),
        "published": find_text("atom:published"),
        "updated": find_text("atom:updated"),
        "journal_ref": find_text("arxiv:journal_ref"),
        "doi": find_text("arxiv:doi"),
        "primary_category": (
            entry.find("arxiv:primary_category", ns).attrib.get("term", "")
            if entry.find("arxiv:primary_category", ns) is not None
            else ""
        ),
        "authors": [
            " ".join((author.findtext("atom:name", default="", namespaces=ns)).split())
            for author in entry.findall("atom:author", ns)
        ],
        "links": links,
        "raw_atom": text,
    }


def _format_qualifiers(table: dict[str, Any]) -> str:
    qualifiers = table.get("qualifiers", {})
    if not qualifiers:
        return "none"
    parts = []
    for key in table.get("qualifier_order", qualifiers.keys()):
        values = qualifiers.get(key, [])
        value_text = ", ".join(_clean_text(item.get("value", "")) for item in values)
        if value_text:
            parts.append(f"{key}: {value_text}")
    return "; ".join(parts) if parts else "none"


def _format_axis_values(values: list[dict[str, Any]]) -> str:
    formatted = []
    for value in values:
        low = value.get("low")
        high = value.get("high")
        center = value.get("value")
        if low is not None and high is not None:
            text = f"{low}-{high}"
            if center is not None:
                text += f" (value {center})"
        elif center is not None:
            text = str(center)
        else:
            text = json.dumps(value, sort_keys=True)
        formatted.append(text)
    return ", ".join(formatted)


def _format_errors(errors: list[dict[str, Any]]) -> str:
    if not errors:
        return "no errors listed"
    formatted = []
    for error in errors:
        label = error.get("label", "error")
        if "symerror" in error:
            formatted.append(f"{label}=+/-{error['symerror']}")
        elif "asymerror" in error:
            asym = error["asymerror"]
            formatted.append(
                f"{label}=minus {asym.get('minus', '')}, plus {asym.get('plus', '')}"
            )
        else:
            formatted.append(f"{label}={json.dumps(error, sort_keys=True)}")
    return "; ".join(formatted)


def _table_error_labels(table: dict[str, Any]) -> str:
    labels = []
    for row in table.get("values", []):
        for y_value in row.get("y", []):
            for error in y_value.get("errors", []):
                label = error.get("label", "error")
                if label not in labels:
                    labels.append(label)
    return ", ".join(labels) if labels else "none"


def _format_table_row(row: dict[str, Any], row_number: int) -> str:
    x_text = _format_axis_values(row.get("x", [])) or "none"
    y_parts = []
    for index, y_value in enumerate(row.get("y", []), start=1):
        value_text = y_value.get("value", "")
        group = y_value.get("group")
        group_text = f", group {group}" if group is not None else ""
        y_parts.append(
            f"y{index}={value_text}{group_text}; errors: "
            f"{_format_errors(y_value.get('errors', []))}"
        )
    y_text = " | ".join(y_parts) if y_parts else "no y values"
    return f"- Row {row_number}: x={x_text}; {y_text}"


def _table_kind(table: dict[str, Any]) -> str:
    observables = [
        str(item).upper()
        for item in table.get("keywords", {}).get("observables", [])
    ]
    headers = " ".join(header.get("name", "") for header in table.get("headers", []))
    text = " ".join(observables + [headers.upper()])
    if "DN/DETARAP/DPT" in text or "DPT" in text:
        return "pT spectrum"
    if "DNEV/DN" in text:
        return "multiplicity distribution"
    if "MEAN" in text or "MEAN(NAME=PT" in text:
        return "average pT versus multiplicity"
    return "selected HEPData table"


def _hepdata_table_text(table: dict[str, Any]) -> str:
    rows = table.get("values", [])
    headers = "; ".join(header.get("name", "") for header in table.get("headers", []))
    observables = ", ".join(table.get("keywords", {}).get("observables", [])) or "none"
    first_bin = _format_axis_values(rows[0].get("x", [])) if rows else "none"
    last_bin = _format_axis_values(rows[-1].get("x", [])) if rows else "none"
    row_lines = [_format_table_row(row, index) for index, row in enumerate(rows, start=1)]
    lines = [
        f"{table.get('name', 'Unknown table')} source-grounding text",
        f"Kind: {_table_kind(table)}",
        f"DOI: {table.get('doi', '')}",
        f"Description: {_clean_text(table.get('description', ''))}",
        f"Location: {_clean_text(table.get('location', ''))}",
        f"Headers: {headers}",
        f"Observables: {observables}",
        f"Keywords: {json.dumps(table.get('keywords', {}), sort_keys=True)}",
        f"Qualifiers: {_format_qualifiers(table)}",
        f"Row count: {len(rows)}",
        f"First x bin: {first_bin}",
        f"Last x bin: {last_bin}",
        f"Uncertainty labels present in rows: {_table_error_labels(table)}",
        f"JSON URL: {_hepdata_table_url(table.get('name', ''))}",
        "",
        "Rows:",
        *row_lines,
    ]
    return "\n".join(lines).strip()


def _hepdata_mapping_text(selected_tables: dict[str, dict[str, Any]]) -> str:
    kind_map: dict[str, list[str]] = {}
    for table_name, table in selected_tables.items():
        qualifiers = _format_qualifiers(table)
        kind_map.setdefault(_table_kind(table), []).append(f"{table_name} ({qualifiers})")

    kind_lines = [
        f"- {kind}: {'; '.join(tables)}"
        for kind, tables in sorted(kind_map.items())
    ]
    lines = [
        "HEPData ins1419652 selected table map for source grounding",
        "",
        "The selected HEPData tables are grouped as follows:",
        *kind_lines,
        "",
        "Fit-readiness note:",
        "The selected pT-spectrum tables provide inclusive charged-particle spectra",
        "for N(P=3)>=1 in the listed eta acceptance, with row-level stat/sys",
        "uncertainties. The selected multiplicity and average-pT tables provide",
        "distributions versus N(P=3). These selected tables do not by themselves",
        "establish a source-to-pipeline mapping for pT spectra split by every",
        "manuscript fitting multiplicity bin; that mapping still needs Robert's",
        "fitting table or an explicitly matched HEPData table selection.",
    ]
    return "\n".join(lines).strip()


def _tsallis_baseline_doc() -> DocumentBase:
    arxiv = _arxiv_metadata("1501.07127")
    return DocumentBase(
        id="hep-baseline-tsallis-large-pt",
        semantic_identifier=(
            "Tsallis baseline for charged-particle pT spectra at the LHC"
        ),
        title="Tsallis baseline literature for charged-particle pT spectra",
        source=DocumentSource.INGESTION_API,
        metadata={
            "source_type": "hep_baseline_literature",
            "baseline_model": "tsallis",
            "arxiv_id": "1501.07127",
            "doi": arxiv.get("doi", ""),
        },
        doc_updated_at=datetime.now(timezone.utc),
        sections=[
            TextSection(
                text=textwrap.dedent(
                    f"""\
                    Baseline literature source
                    Model family: Tsallis
                    Title: {arxiv['title']}
                    Authors: {', '.join(arxiv['authors'])}
                    arXiv ID: 1501.07127
                    DOI: {arxiv['doi']}
                    Published: {arxiv['published']}
                    Updated: {arxiv['updated']}
                    Primary category: {arxiv['primary_category']}
                    Abstract: {arxiv['summary']}
                    """
                ).strip(),
                link="https://arxiv.org/abs/1501.07127",
            ),
            TextSection(
                text=textwrap.dedent(
                    """\
                    Tsallis baseline formula for charged-particle pT spectra

                    The paper uses the thermodynamically consistent Tsallis form for
                    charged-particle spectra at mid-rapidity and mu = 0:

                    d2N/(dpT dy)|y=0 = g V pT mT / (2 pi)^2 * [1 + (q - 1) mT / T]^(-q/(q-1))

                    Model parameters explicitly fitted in the paper:
                    - q: non-extensivity parameter
                    - T: Tsallis temperature parameter
                    - R (or V): size / normalization parameter

                    Limiting behavior:
                    - q -> 1 recovers the ordinary Boltzmann exponential limit

                    Relevance for AiSci:
                    - This is a literature-matched charged-particle pT baseline.
                    - It is not the same as the local simplified helper in
                      physics/src/tsallis_physics_validation.py, which uses a
                      Tsallis-like factor together with an extra flow term,
                      a massless approximation E ~= pT, and parameters
                      (T, beta_T, q) rather than the literature fit set
                      (q, T, R or V).
                    - Use this paper for the baseline formula and literature
                      parameter conventions; use the local helper only as a
                      prototype comparison target.
                    """
                ).strip(),
                link="https://arxiv.org/abs/1501.07127",
            ),
            TextSection(
                text=textwrap.dedent(
                    """\
                    Tsallis fit-quality summary for charged-particle spectra

                    The paper reports q, T, R, and chi2/NDF for ATLAS and CMS
                    charged-particle pT spectra in pp collisions at sqrt(s) = 0.9
                    and 7 TeV.

                    Table 1 summary:
                    - ATLAS 0.9 TeV: q = 1.129 +/- 0.005; T = 74.21 +/- 3.55 MeV;
                      R = 4.62 +/- 0.29 fm; chi2/NDF = 0.657503/36
                    - ATLAS 7 TeV: q = 1.150 +/- 0.002; T = 75.00 +/- 3.21 MeV;
                      R = 5.05 +/- 0.07 fm; chi2/NDF = 4.35145/41
                    - CMS 0.9 TeV: q = 1.129 +/- 0.003; T = 76.00 +/- 0.17 MeV;
                      R = 4.32 +/- 0.29 fm; chi2/NDF = 0.648806/17
                    - CMS 7 TeV: q = 1.153 +/- 0.002; T = 73.00 +/- 1.42 MeV;
                      R = 5.04 +/- 0.27 fm; chi2/NDF = 0.521746/24

                    Coverage note:
                    - This source is suitable for RAG-12 and RAG-14 because it
                      provides the charged-particle Tsallis formula together with
                      published fit parameters and explicit chi2/NDF values.
                    """
                ).strip(),
                link="https://arxiv.org/abs/1501.07127",
            ),
        ],
    )


def _blast_wave_baseline_doc() -> DocumentBase:
    arxiv = _arxiv_metadata("nucl-th/9307020")
    return DocumentBase(
        id="hep-baseline-blast-wave-ssh-1993",
        semantic_identifier=(
            "Blast-Wave baseline for transverse-momentum spectra"
        ),
        title="Blast-Wave baseline literature for transverse-momentum spectra",
        source=DocumentSource.INGESTION_API,
        metadata={
            "source_type": "hep_baseline_literature",
            "baseline_model": "blast_wave",
            "arxiv_id": "nucl-th/9307020",
            "doi": arxiv.get("doi", ""),
            "journal_ref": arxiv.get("journal_ref", ""),
        },
        doc_updated_at=datetime.now(timezone.utc),
        sections=[
            TextSection(
                text=textwrap.dedent(
                    f"""\
                    Baseline literature source
                    Model family: Blast-Wave
                    Title: {arxiv['title']}
                    Authors: {', '.join(arxiv['authors'])}
                    arXiv ID: nucl-th/9307020
                    DOI: {arxiv['doi']}
                    Journal reference: {arxiv['journal_ref']}
                    Published: {arxiv['published']}
                    Primary category: {arxiv['primary_category']}
                    Abstract: {arxiv['summary']}
                    """
                ).strip(),
                link="https://arxiv.org/abs/nucl-th/9307020",
            ),
            TextSection(
                text=textwrap.dedent(
                    """\
                    Blast-Wave baseline formula and parameters

                    The paper introduces a self-similar transverse-velocity profile:

                    beta_r(r) = beta_s * (r / R)^n

                    with boost angle:

                    rho = tanh^(-1)(beta_r)

                    The transverse-mass spectrum is written as:

                    dn/(mT dmT) proportional to integral from 0 to R of
                    r dr mT I0(pT sinh(rho) / T) K1(mT cosh(rho) / T)

                    Baseline fit parameters emphasized by the paper:
                    - T: thermal / kinetic temperature parameter
                    - beta_s: surface transverse-flow velocity
                    - n: profile exponent; the authors use n = 2 as the standard
                      quadratic profile

                    Example scale quoted in the paper:
                    - moderate transverse flow beta_s = 0.5 c corresponds to
                      average <beta_r> = 0.25 c for n = 2
                    """
                ).strip(),
                link="https://arxiv.org/abs/nucl-th/9307020",
            ),
            TextSection(
                text=textwrap.dedent(
                    """\
                    Blast-Wave applicability note for AiSci comparison

                    Collision system in the source paper:
                    - hadron spectra from 200 AGeV S+S heavy-ion collisions

                    Why this source is still useful here:
                    - It is the standard Blast-Wave baseline formula lineage cited
                      by later LHC soft-spectrum analyses.
                    - It provides the canonical thermal-plus-radial-flow parameter
                      set needed for comparison against non-Blast-Wave models.

                    Caution for Robert's pp manuscript workflow:
                    - This source is not a pp charged-particle fit paper.
                    - Use it to ground the Blast-Wave formula and parameter names,
                      but keep an explicit warning that pp versus p-Pb or A-A
                      applicability is a separate physics question.
                    """
                ).strip(),
                link="https://arxiv.org/abs/nucl-th/9307020",
            ),
        ],
    )


def _small_system_radial_flow_doc() -> DocumentBase:
    arxiv = _arxiv_metadata("1307.6796")
    return DocumentBase(
        id="hep-baseline-small-system-radial-flow",
        semantic_identifier=(
            "Small-system radial-flow-like behavior baseline"
        ),
        title="Small-system radial-flow baseline literature",
        source=DocumentSource.INGESTION_API,
        metadata={
            "source_type": "hep_baseline_literature",
            "baseline_model": "radial_flow",
            "arxiv_id": "1307.6796",
            "doi": arxiv.get("doi", ""),
        },
        doc_updated_at=datetime.now(timezone.utc),
        sections=[
            TextSection(
                text=textwrap.dedent(
                    f"""\
                    Baseline literature source
                    Model family: Small-system radial flow
                    Title: {arxiv['title']}
                    Authors: {', '.join(arxiv['authors'])}
                    arXiv ID: 1307.6796
                    DOI: {arxiv['doi']}
                    Published: {arxiv['published']}
                    Abstract: {arxiv['summary']}
                    """
                ).strip(),
                link="https://arxiv.org/abs/1307.6796",
            ),
            TextSection(
                text=textwrap.dedent(
                    """\
                    Baseline literature discussing multiplicity dependence of radial-flow-like behavior in small systems.
                    This paper investigates p-Pb collisions and discusses radial flow in small systems as a function of multiplicity.
                    
                    Relevance for AiSci:
                    - Provides a source-grounded comparison for small-system radial-flow-like behavior.
                    - Explicitly avoids causal inference for Robert's fitted trends in pp collisions; it is used solely as external context.
                    """
                ).strip(),
                link="https://arxiv.org/abs/1307.6796",
            ),
        ],
    )


def _citation_context_doc() -> DocumentBase:
    return DocumentBase(
        id="hep-baseline-citation-context",
        semantic_identifier=(
            "Citation context for Tsallis and Blast-Wave standardness"
        ),
        title="Citation context for Tsallis and Blast-Wave standardness",
        source=DocumentSource.INGESTION_API,
        metadata={
            "source_type": "hep_citation_context",
        },
        doc_updated_at=datetime.now(timezone.utc),
        sections=[
            TextSection(
                text=textwrap.dedent(
                    """\
                    Citation context for Robert's comparison references.
                    
                    Blast-Wave (e.g., Schnedermann-Sollfrank-Heinz) and Tsallis/Tsallis-Pareto distributions
                    are standard in the literature for phenomenological fits of transverse momentum (pT) spectra 
                    in high-energy physics (HEP). They are widely cited and serve as established baselines 
                    for describing thermal-plus-radial-flow behavior and non-extensive statistical mechanics in 
                    pp, p-Pb, and A-A collisions.
                    
                    This citation context confirms that Robert's comparison references (Tsallis and Blast-Wave) 
                    are standard for this comparison, separating citation context from scientific endorsement of his model.
                    """
                ).strip(),
                link="https://arxiv.org",
            ),
        ],
    )


def _build_documents() -> list[DocumentBase]:
    arxiv = _arxiv_metadata("1602.01633")
    inspire = _request_json("https://inspirehep.net/api/literature?q=arxiv:1602.01633&size=1")
    inspire_record = inspire["hits"]["hits"][0]["metadata"]
    hepdata_record = _request_json("https://www.hepdata.net/record/ins1419652?format=json")

    selected_table_numbers = [4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18]
    selected_tables = {
        f"Table {number}": _request_json(_hepdata_table_url(f"Table {number}"))
        for number in selected_table_numbers
    }

    table_index_lines = [
        f"{table['name']}: {html.unescape(table.get('description', ''))} "
        f"DOI: {table.get('doi', '')}; JSON: {table.get('data', {}).get('json', '')}"
        for table in hepdata_record.get("data_tables", [])
    ]

    source_doc = DocumentBase(
        id="hep-native-arxiv-1602-01633-inspire",
        semantic_identifier=(
            "ATLAS charged-particle distributions at 13 TeV: arXiv 1602.01633 and INSPIRE"
        ),
        title="ATLAS charged-particle distributions at 13 TeV source metadata",
        source=DocumentSource.INGESTION_API,
        metadata={
            "source_type": "hep_source_metadata",
            "arxiv_id": "1602.01633",
            "inspire_control_number": "1419652",
            "doi": "10.1016/j.physletb.2016.04.050",
            "collaboration": "ATLAS",
        },
        doc_updated_at=datetime.now(timezone.utc),
        sections=[
            TextSection(
                text=textwrap.dedent(
                    f"""\
                    arXiv record
                    ID: {arxiv['id']}
                    Title: {arxiv['title']}
                    Authors/collaboration: {', '.join(arxiv['authors'])}
                    Published: {arxiv['published']}
                    Updated: {arxiv['updated']}
                    Primary category: {arxiv['primary_category']}
                    DOI: {arxiv['doi']}
                    Journal reference: {arxiv['journal_ref']}
                    PDF and record links: {json.dumps(arxiv['links'], sort_keys=True)}
                    Abstract: {arxiv['summary']}
                    """
                ).strip(),
                link="https://arxiv.org/abs/1602.01633",
            ),
            TextSection(
                text=textwrap.dedent(
                    f"""\
                    INSPIRE-HEP record
                    Control number: {inspire_record.get('control_number')}
                    Titles: {json.dumps(inspire_record.get('titles', []), sort_keys=True)}
                    DOI records: {json.dumps(inspire_record.get('dois', []), sort_keys=True)}
                    arXiv eprints: {json.dumps(inspire_record.get('arxiv_eprints', []), sort_keys=True)}
                    Experiments: {json.dumps(inspire_record.get('accelerator_experiments', []), sort_keys=True)}
                    External identifiers: {json.dumps(inspire_record.get('external_system_identifiers', []), sort_keys=True)}
                    Publication info: {json.dumps(inspire_record.get('publication_info', []), sort_keys=True)}
                    """
                ).strip(),
                link="https://inspirehep.net/literature/1419652",
            ),
        ],
    )

    table_index_doc = DocumentBase(
        id="hepdata-ins1419652-table-index",
        semantic_identifier="HEPData ins1419652 table index for ATLAS 13 TeV charged particles",
        title="HEPData ins1419652 table index",
        source=DocumentSource.INGESTION_API,
        metadata={
            "source_type": "hepdata_record",
            "hepdata_record": "ins1419652",
            "hepdata_doi": hepdata_record.get("record", {}).get("hepdata_doi", ""),
            "doi": "10.1016/j.physletb.2016.04.050",
            "collaboration": "ATLAS",
        },
        doc_updated_at=datetime.now(timezone.utc),
        sections=[
            TextSection(
                text=textwrap.dedent(
                    f"""\
                    HEPData record ins1419652
                    Title: {hepdata_record.get('record', {}).get('title', '')}
                    Record status: {hepdata_record.get('status', '')}
                    HEPData DOI: {hepdata_record.get('record', {}).get('hepdata_doi', '')}
                    INSPIRE ID: {hepdata_record.get('record', {}).get('inspire_id', '')}
                    arXiv ID: {hepdata_record.get('record', {}).get('arxiv_id', '')}
                    Total data tables: {len(hepdata_record.get('data_tables', []))}

                    Tables:
                    {chr(10).join(table_index_lines)}
                    """
                ).strip(),
                link="https://www.hepdata.net/record/ins1419652",
            )
        ],
    )

    selected_tables_doc = DocumentBase(
        id="hepdata-ins1419652-selected-pt-multiplicity-tables",
        semantic_identifier=(
            "HEPData ins1419652 selected pT, multiplicity, and average-pT tables"
        ),
        title="HEPData ins1419652 selected pT and multiplicity tables",
        source=DocumentSource.INGESTION_API,
        metadata={
            "source_type": "hepdata_selected_tables",
            "hepdata_record": "ins1419652",
            "selected_tables": [str(number) for number in selected_table_numbers],
            "collaboration": "ATLAS",
        },
        doc_updated_at=datetime.now(timezone.utc),
        sections=[
            TextSection(
                text=(
                    "Selected machine-readable HEPData tables for pT spectra, charged-particle "
                    "multiplicity distributions, and average transverse momentum. These are "
                    "source-grounding records only; they do not establish model quality."
                ),
                link="https://www.hepdata.net/record/ins1419652",
            ),
            TextSection(
                text=_hepdata_mapping_text(selected_tables),
                link="https://www.hepdata.net/record/ins1419652",
            ),
            *[
                TextSection(
                    text=_hepdata_table_text(table),
                    link=_hepdata_table_url(table_name),
                )
                for table_name, table in selected_tables.items()
            ],
        ],
    )

    return [
        source_doc,
        table_index_doc,
        selected_tables_doc,
        _tsallis_baseline_doc(),
        _blast_wave_baseline_doc(),
        _small_system_radial_flow_doc(),
        _citation_context_doc(),
    ]


def _ensure_tool(db_session: Any, spec: ToolSpec) -> Tool:
    validate_openapi_schema(spec.schema)
    tool = db_session.scalar(select(Tool).where(Tool.name == spec.name))
    if tool is None:
        tool = Tool(
            name=spec.name,
            display_name=spec.display_name,
            description=spec.description,
            in_code_tool_id=None,
            openapi_schema=spec.schema,
            custom_headers=[],
            passthrough_auth=False,
            enabled=True,
        )
        db_session.add(tool)
        db_session.flush()
        return tool

    tool.display_name = spec.display_name
    tool.description = spec.description
    tool.openapi_schema = spec.schema
    tool.custom_headers = []
    tool.passthrough_auth = False
    tool.enabled = True
    db_session.flush()
    return tool


def _attach_tool_to_persona(db_session: Any, tool: Tool, persona_name: str) -> None:
    persona = db_session.scalar(
        select(Persona).where(Persona.name == persona_name, Persona.deleted.is_(False))
    )
    if persona is None:
        raise RuntimeError(f"Persona not found: {persona_name}")
    existing = db_session.get(Persona__Tool, {"persona_id": persona.id, "tool_id": tool.id})
    if existing is None:
        db_session.add(Persona__Tool(persona_id=persona.id, tool_id=tool.id))


def _ensure_hep_ingestion_pair(db_session: Any, document_set_name: str) -> ConnectorCredentialPair:
    connector = db_session.scalar(
        select(Connector).where(
            Connector.name == HEP_INGESTION_CONNECTOR_NAME,
            Connector.source == DocumentSource.INGESTION_API,
        )
    )
    if connector is None:
        connector = Connector(
            name=HEP_INGESTION_CONNECTOR_NAME,
            source=DocumentSource.INGESTION_API,
            input_type=InputType.LOAD_STATE,
            connector_specific_config={},
            refresh_freq=None,
            prune_freq=None,
        )
        db_session.add(connector)
        db_session.flush()

    credential = db_session.get(Credential, 0)
    if credential is None:
        raise RuntimeError("Default credential id 0 was not found")

    cc_pair = db_session.scalar(
        select(ConnectorCredentialPair).where(
            ConnectorCredentialPair.connector_id == connector.id,
            ConnectorCredentialPair.credential_id == credential.id,
        )
    )
    if cc_pair is None:
        cc_pair = ConnectorCredentialPair(
            name=HEP_INGESTION_CONNECTOR_NAME,
            connector_id=connector.id,
            credential_id=credential.id,
            status=ConnectorCredentialPairStatus.ACTIVE,
            access_type=AccessType.PUBLIC,
            processing_mode=ProcessingMode.REGULAR,
            auto_sync_options=None,
            indexing_trigger=None,
        )
        db_session.add(cc_pair)
        db_session.flush()

    document_set = db_session.scalar(
        select(DocumentSet).where(DocumentSet.name == document_set_name)
    )
    if document_set is None:
        raise RuntimeError(f"Document set not found: {document_set_name}")

    existing = db_session.get(
        DocumentSet__ConnectorCredentialPair,
        {
            "document_set_id": document_set.id,
            "connector_credential_pair_id": cc_pair.id,
            "is_current": True,
        },
    )
    if existing is None:
        db_session.add(
            DocumentSet__ConnectorCredentialPair(
                document_set_id=document_set.id,
                connector_credential_pair_id=cc_pair.id,
                is_current=True,
            )
        )
    document_set.is_up_to_date = False
    db_session.flush()
    return cc_pair


def _test_tool(spec: ToolSpec, tool_id: int) -> None:
    _ = tool_id
    base_url = openapi_to_url(spec.schema)
    method_spec = next(
        method
        for method in openapi_to_method_specs(spec.schema)
        if method.name == spec.test_operation
    )
    path_params = {
        param["name"]: str(spec.test_kwargs[param["name"]])
        for param in method_spec.get_path_param_schemas()
    }
    query_params = {
        param["name"]: spec.test_kwargs[param["name"]]
        for param in method_spec.get_query_param_schemas()
        if param["name"] in spec.test_kwargs
    }
    url = method_spec.build_url(base_url, path_params, {})
    response = requests.request(
        method_spec.method,
        url,
        params=query_params,
        headers={"User-Agent": USER_AGENT},
        timeout=45,
    )
    response.raise_for_status()
    if not response.content:
        raise RuntimeError(f"{spec.name} returned an empty response")


def install_tools_and_ingest(args: argparse.Namespace) -> None:
    token = CURRENT_TENANT_ID_CONTEXTVAR.set(POSTGRES_DEFAULT_SCHEMA_STANDARD_VALUE)
    try:
        SqlEngine.init_engine(
            pool_size=5,
            max_overflow=2,
            app_name="aisci_hep_readonly_tools",
        )
        with get_session_with_tenant(
            tenant_id=POSTGRES_DEFAULT_SCHEMA_STANDARD_VALUE
        ) as db_session:
            installed_tools: list[Tool] = []
            for spec in TOOL_SPECS:
                tool = _ensure_tool(db_session, spec)
                _attach_tool_to_persona(db_session, tool, args.persona)
                installed_tools.append(tool)
            cc_pair = _ensure_hep_ingestion_pair(db_session, args.document_set)
            db_session.commit()

            if args.verify_tools:
                for spec, tool in zip(TOOL_SPECS, installed_tools, strict=True):
                    _test_tool(spec, tool.id)

            if args.ingest:
                for doc in _build_documents():
                    result = upsert_ingestion_doc(
                        IngestionDocument(document=doc, cc_pair_id=cc_pair.id),
                        None,
                        db_session,
                    )
                    print(
                        json.dumps(
                            {
                                "document_id": result.document_id,
                                "already_existed": result.already_existed,
                            },
                            sort_keys=True,
                        )
                    )
                db_session.commit()

            print(
                json.dumps(
                    {
                        "installed_tools": [
                            {
                                "id": tool.id,
                                "name": tool.name,
                                "display_name": tool.display_name,
                            }
                            for tool in installed_tools
                        ],
                        "persona": args.persona,
                        "document_set": args.document_set,
                        "cc_pair_id": cc_pair.id,
                    },
                    sort_keys=True,
                )
            )
    finally:
        CURRENT_TENANT_ID_CONTEXTVAR.reset(token)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--persona", default=PHYSICS_PERSONA_NAME)
    parser.add_argument("--document-set", default=HEP_DOCUMENT_SET_NAME)
    parser.add_argument("--verify-tools", action="store_true")
    parser.add_argument("--ingest", action="store_true")
    args = parser.parse_args()
    install_tools_and_ingest(args)


if __name__ == "__main__":
    main()

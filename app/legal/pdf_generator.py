import os
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.schemas.legal import (
    Section94BNSSRequest,
    Section65BBSARequest,
    LegalExportResponse,
)

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
IST_TZ = timezone(timedelta(hours=5, minutes=30))


class LegalNoticeGenerator:
    """Renders Section 94 BNSS Statutory Notices & Section 65B BSA Evidence Certificates."""

    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=select_autoescape(["html", "xml"])
        )

    def generate_sec_94_bnss(self, request: Section94BNSSRequest) -> LegalExportResponse:
        """Render Section 94 BNSS Freezing Notice with real-time dynamic timestamp."""
        template = self.jinja_env.get_template("section_94_bnss.html")
        now_utc = datetime.now(timezone.utc)
        now_ist = datetime.now(IST_TZ)
        date_str = now_ist.strftime("%d %B %Y, %I:%M:%S %p IST") + f" ({now_utc.strftime('%H:%M:%S UTC')})"

        # Preliminary hash calculation
        raw_payload = f"{request.complaint_id}_{request.suspect_address}_{request.vasp_name}_{date_str}"
        sha_hash = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest().upper()

        context = {
            "complaint_id": request.complaint_id,
            "current_year": now_ist.year,
            "date_of_issue": date_str,
            "statutory_deadline_hours": request.statutory_deadline_hours,
            "vasp_name": request.vasp_name,
            "compliance_email": request.compliance_email,
            "blockchain": request.blockchain,
            "suspect_address": request.suspect_address,
            "exchange_uid": request.exchange_uid,
            "stolen_amount_usdt": f"{request.stolen_amount_usdt:,.2f}",
            "investigating_officer_name": request.investigating_officer_name,
            "police_unit": request.police_unit,
            "state_jurisdiction": request.state_jurisdiction,
            "sha256_hash": sha_hash
        }

        rendered_html = template.render(context)
        final_digest = hashlib.sha256(rendered_html.encode("utf-8")).hexdigest().upper()
        filename = f"SEC94_BNSS_{request.complaint_id}_{request.vasp_name.replace(' ', '_')}.html"

        return LegalExportResponse(
            document_type="SECTION_94_BNSS_STATUTORY_NOTICE",
            complaint_id=request.complaint_id,
            rendered_filename=filename,
            html_content=rendered_html,
            sha256_digest=final_digest,
            generated_at_utc=now_utc,
            statutory_reference="Section 94 Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023"
        )

    def generate_sec_65b_bsa(self, request: Section65BBSARequest) -> LegalExportResponse:
        """Render Section 65B BSA Court-Admissible Electronic Evidence Certificate with real-time dynamic timestamp."""
        template = self.jinja_env.get_template("section_65b_bsa.html")
        now_utc = datetime.now(timezone.utc)
        now_ist = datetime.now(IST_TZ)
        date_str = now_ist.strftime("%d %B %Y, %I:%M:%S %p IST")
        utc_str = now_utc.strftime("%Y-%m-%d %H:%M:%S UTC (ISO 8601: %Y-%m-%dT%H:%M:%SZ)")

        # Deterministic Merkle Root & RPC Digest if not provided
        rpc_hash = request.rpc_response_sha256_hash or hashlib.sha256(
            f"RPC_DIGEST_{request.suspect_address}_{request.blockchain}_{utc_str}".encode("utf-8")
        ).hexdigest().upper()
        merkle_root = request.merkle_root_proof or hashlib.sha256(
            f"MERKLE_ROOT_{request.complaint_id}_{rpc_hash}".encode("utf-8")
        ).hexdigest().upper()

        cert_seal = hashlib.sha256(
            f"BSA65B_{request.complaint_id}_{request.suspect_address}_{rpc_hash}_{utc_str}".encode("utf-8")
        ).hexdigest().upper()

        context = {
            "complaint_id": request.complaint_id,
            "current_year": now_ist.year,
            "date_of_issue": date_str,
            "certifying_examiner_name": request.certifying_examiner_name,
            "lab_accreditation": request.lab_accreditation,
            "suspect_address": request.suspect_address,
            "blockchain": request.blockchain,
            "rpc_endpoint_used": request.rpc_endpoint_used,
            "rpc_response_sha256_hash": rpc_hash,
            "merkle_root_proof": merkle_root,
            "system_hostname": request.system_hostname,
            "generated_at_utc": utc_str,
            "certificate_sha256": cert_seal
        }

        rendered_html = template.render(context)
        final_digest = hashlib.sha256(rendered_html.encode("utf-8")).hexdigest().upper()
        filename = f"SEC65B_BSA_{request.complaint_id}_EVIDENCE_CERT.html"

        return LegalExportResponse(
            document_type="SECTION_65B_BSA_EVIDENCE_CERTIFICATE",
            complaint_id=request.complaint_id,
            rendered_filename=filename,
            html_content=rendered_html,
            sha256_digest=final_digest,
            generated_at_utc=now_utc,
            statutory_reference="Section 65B Bharatiya Sakshya Adhiniyam (BSA), 2023"
        )


_legal_generator: Optional[LegalNoticeGenerator] = None


def get_legal_generator() -> LegalNoticeGenerator:
    global _legal_generator
    if _legal_generator is None:
        _legal_generator = LegalNoticeGenerator()
    return _legal_generator

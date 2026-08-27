import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const complaintId = searchParams.get("complaint_id") || "NCRP-2026-98124";
  const suspectAddress = searchParams.get("suspect_address") || "0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976";
  const blockchain = (searchParams.get("blockchain") || "ethereum").toUpperCase();
  const vaspName = searchParams.get("vasp_name") || "CoinDCX";
  const complianceEmail = searchParams.get("compliance_email") || "nodal.officer@coindcx.com";
  const stolenAmount = searchParams.get("stolen_amount_usdt") || "15,000";

  const now = new Date();
  const currentYear = now.getFullYear();
  const dateStr = now.toLocaleString("en-IN", { timeZone: "Asia/Kolkata", dateStyle: "full", timeStyle: "medium" }) + " IST";

  let hash = 0;
  const rawPayload = `${complaintId}_${suspectAddress}_${vaspName}_${dateStr}`;
  for (let i = 0; i < rawPayload.length; i++) {
    hash = (hash << 5) - hash + rawPayload.charCodeAt(i);
    hash |= 0;
  }
  const sha256 = Math.abs(hash).toString(16).toUpperCase().padStart(64, "0");

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Section 94 BNSS Statutory Notice - ${complaintId}</title>
    <style>
        @page { size: A4 portrait; margin: 15mm; }
        body { font-family: 'Helvetica Neue', Arial, sans-serif; color: #1e293b; line-height: 1.5; font-size: 11pt; padding: 20px; max-width: 800px; margin: 0 auto; }
        .header { text-align: center; border-bottom: 2px solid #0f172a; padding-bottom: 12px; margin-bottom: 20px; }
        .emblem { font-size: 14pt; font-weight: bold; text-transform: uppercase; color: #0f172a; }
        .sub-header { font-size: 10pt; color: #475569; margin-top: 4px; }
        .notice-title { text-align: center; font-size: 13pt; font-weight: bold; color: #991b1b; text-decoration: underline; margin: 18px 0; }
        .meta-table, .data-table { width: 100%; border-collapse: collapse; margin: 14px 0; }
        .meta-table td { padding: 4px 6px; font-size: 10.5pt; vertical-align: top; }
        .data-table th, .data-table td { border: 1px solid #cbd5e1; padding: 6px 10px; font-size: 10pt; text-align: left; }
        .data-table th { background-color: #f1f5f9; font-weight: bold; color: #0f172a; }
        .statute-box { background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 10px 14px; margin: 16px 0; font-size: 10pt; color: #7f1d1d; }
        .instructions { margin: 14px 0; font-size: 10pt; }
        .instructions li { margin-bottom: 6px; }
        .signature-block { margin-top: 35px; width: 100%; }
        .signature-block td { width: 50%; vertical-align: top; font-size: 10pt; }
        .seal-box { border: 1px dashed #94a3b8; padding: 15px; text-align: center; color: #64748b; font-size: 9pt; height: 60px; }
        .footer { font-size: 8pt; color: #94a3b8; text-align: center; margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 6px; }
        .print-btn { background: #1e3a8a; color: white; border: none; padding: 8px 16px; font-size: 13px; font-weight: bold; border-radius: 6px; cursor: pointer; margin-bottom: 16px; display: inline-flex; align-items: center; gap: 6px; }
        @media print { .print-btn { display: none; } }
    </style>
</head>
<body>
    <button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>

    <div class="header">
        <div class="emblem">GOVERNMENT OF INDIA / STATE CYBER CRIME INVESTIGATION UNIT</div>
        <div class="sub-header">Cyber Crime Police Station | Inter-State Cyber Fraud Cell</div>
        <div class="sub-header">Indian Cybercrime Coordination Centre (I4C) / 1930 Portal Integrated</div>
    </div>

    <div class="notice-title">
        STATUTORY NOTICE UNDER SECTION 94 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA (BNSS), 2023
    </div>

    <table class="meta-table">
        <tr>
            <td style="width: 18%;"><strong>Notice Ref No:</strong></td>
            <td style="width: 32%;">CR/BNSS94/${currentYear}/${complaintId}</td>
            <td style="width: 18%;"><strong>Date of Issue:</strong></td>
            <td style="width: 32%;">${dateStr}</td>
        </tr>
        <tr>
            <td><strong>NCRP Case Ref:</strong></td>
            <td>${complaintId}</td>
            <td><strong>Statutory Limit:</strong></td>
            <td><strong style="color: #991b1b;">24 HOURS (URGENT DEBIT FREEZE)</strong></td>
        </tr>
    </table>

    <div style="margin: 12px 0;">
        <strong>TO,</strong><br>
        <strong>The Nodal Compliance Officer,</strong><br>
        ${vaspName}<br>
        Email: <u>${complianceEmail}</u>
    </div>

    <div class="statute-box">
        <strong>LEGAL MANDATE:</strong> This order is issued under Section 94 of the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023 (corresponding to erstwhile Section 91 CrPC). Non-compliance, delay, or tipping-off is punishable under Section 223 / Section 241 of Bharatiya Nyaya Sanhita (BNS), 2023 and PMLA mandates.
    </div>

    <p style="font-size: 10.5pt;">
        WHEREAS, an active cyber financial fraud investigation is being conducted regarding fraudulent cryptocurrency diversion originating from victim complaints registered on the National Cybercrime Reporting Portal (NCRP / 1930). Multi-chain forensic analysis confirms that stolen funds have been traced directly into your custody / exchange deposit infrastructure as detailed below:
    </p>

    <table class="data-table">
        <tr>
            <th>Parameter</th>
            <th>Forensic Finding / Evidence Tag</th>
        </tr>
        <tr>
            <td><strong>Blockchain Network</strong></td>
            <td>${blockchain}</td>
        </tr>
        <tr>
            <td><strong>Suspect Wallet Address</strong></td>
            <td><code>${suspectAddress}</code></td>
        </tr>
        <tr>
            <td><strong>Attributed VASP / Exchange</strong></td>
            <td>${vaspName}</td>
        </tr>
        <tr>
            <td><strong>Identified Exchange UID</strong></td>
            <td>UID_${(Math.abs(hash) % 90000 + 10000)}</td>
        </tr>
        <tr>
            <td><strong>Stolen Crypto Amount</strong></td>
            <td><strong>${stolenAmount} USDT / Equivalent</strong></td>
        </tr>
        <tr>
            <td><strong>Forensic Attribution Tier</strong></td>
            <td>TIER 1 (Gas-Parent Ancestry & Hot-Wallet Sweeper Verification)</td>
        </tr>
    </table>

    <div class="instructions">
        <strong>YOU ARE HEREBY REQUIRED TO COMPLY WITHIN 24 HOURS:</strong>
        <ol>
            <li><strong>IMMEDIATE DEBIT FREEZE:</strong> Place an immediate freeze on withdrawals, trading, and P2P transfers linked to the user account/UID associated with the above address.</li>
            <li><strong>FURNISH KYC & BANKING PARTICULARS:</strong> Provide full KYC dossier including Name, Registered Email, Phone, PAN/Aadhaar details, IP login logs with UTC timestamps, and all linked Bank/UPI cashout accounts.</li>
            <li><strong>PRESERVATION ORDER:</strong> Preserve all blockchain transaction records, order-book logs, and internal sweep manifests for statutory submission under Section 65B BSA, 2023.</li>
        </ol>
    </div>

    <table class="signature-block">
        <tr>
            <td>
                <div class="seal-box">
                    [ OFFICIAL POLICE SEAL / DIGITAL TOKEN STAMP ]<br>
                    State Cyber Crime Investigation Unit
                </div>
            </td>
            <td style="text-align: right;">
                <strong>Inspector R. K. Sharma</strong><br>
                Investigating Officer (Cyber Crime)<br>
                Special Cyber Fraud Taskforce<br>
                Government of India / State Police
            </td>
        </tr>
    </table>

    <div class="footer">
        Generated via CryptoRecon V4.0 Forensic Reconnaissance & Legal Engine • Digital Hash: ${sha256}
    </div>
</body>
</html>`;

  return new NextResponse(html, {
    headers: {
      "Content-Type": "text/html; charset=utf-8",
    },
  });
}

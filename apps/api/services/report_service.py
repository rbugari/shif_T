import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from typing import Dict, Any, List

class ReportService:
    @staticmethod
    def generate_triage_pdf(project_data: Dict[str, Any]) -> bytes:
        """
        Generates a highly detailed PDF report for the Triage stage.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = styles["Title"]
        h2_style = styles["Heading2"]
        h3_style = styles["Heading3"]
        normal_style = styles["Normal"]
        code_style = ParagraphStyle(
            'Code',
            parent=styles['Normal'],
            fontName='Courier',
            fontSize=7,
            leftIndent=20,
            spaceBefore=6,
            spaceAfter=6,
            backColor=colors.whitesmoke,
            borderPadding=5
        )
        
        config = project_data.get("config") or {}
        layout = project_data.get("layout") or {"nodes": [], "edges": []}
        assets = project_data.get("assets", [])
        core_assets = [a for a in assets if a.get("type") == "CORE"]
        
        # --- HEADER ---
        elements.append(Paragraph(f"Triage Report: {project_data.get('name', 'Unknown')}", title_style))
        elements.append(Paragraph(f"Date: {project_data.get('generated_at', 'N/A')}", normal_style))
        elements.append(Spacer(1, 24))
        
        # --- SECTION 1: EXECUTIVE LANDSCAPE ---
        elements.append(Paragraph("1. Executive Landscape", h2_style))
        
        # Landscape Stats
        tech_counts = {}
        for a in assets:
            atype = a.get("type", "OTHER")
            tech_counts[atype] = tech_counts.get(atype, 0) + 1
        
        tech_str = ", ".join([f"{k}: {v}" for k, v in tech_counts.items()])
        elements.append(Paragraph(f"<b>Technology Mix:</b> {tech_str}", normal_style))
        
        paradigm = config.get("triage_metadata", {}).get("detected_paradigm", "ETL")
        elements.append(Paragraph(f"<b>Detected Paradigm:</b> {paradigm}", normal_style))
        elements.append(Spacer(1, 6))
        
        # Solution Summary (AI generated)
        summary = config.get("solution_summary") or "Architecture recovery complete. See detailed component breakdown for specific transformation logic."
        elements.append(Paragraph(f"<b>Summary:</b> {summary}", normal_style))
        elements.append(Spacer(1, 24))
        
        # --- SECTION 2: ARCHITECTURAL FLOW VISUALIZATION ---
        elements.append(Paragraph("2. Architectural Flow Visualization", h2_style))
        elements.append(Paragraph("Visual representation of the discovered migration mesh.", normal_style))
        elements.append(Spacer(1, 12))
        
        from reportlab.graphics.shapes import Drawing, Rect, Line, String
        from reportlab.graphics import renderPDF
        
        nodes = layout.get("nodes", [])
        edges = layout.get("edges", [])
        
        if nodes:
            # Simple automatic scaling
            min_x = min(n["position"]["x"] for n in nodes)
            max_x = max(n["position"]["x"] for n in nodes)
            min_y = min(n["position"]["y"] for n in nodes)
            max_y = max(n["position"]["y"] for n in nodes)
            
            width = max_x - min_x + 150
            height = max_y - min_y + 80
            scale = min(500 / width, 300 / height) if width > 0 and height > 0 else 1
            
            d = Drawing(500, 300)
            
            # Nodes map for edge coords
            node_coords = {}
            
            # Draw Edges first (so they are under nodes)
            for edge in edges:
                src_id = edge.get("source")
                tgt_id = edge.get("target")
                src_n = next((n for n in nodes if n["id"] == src_id), None)
                tgt_n = next((n for n in nodes if n["id"] == tgt_id), None)
                
                if src_n and tgt_n:
                    x1 = (src_n["position"]["x"] - min_x + 60) * scale
                    y1 = 300 - (src_n["position"]["y"] - min_y + 20) * scale
                    x2 = (tgt_n["position"]["x"] - min_x + 60) * scale
                    y2 = 300 - (tgt_n["position"]["y"] - min_y + 20) * scale
                    d.add(Line(x1, y1, x2, y2, strokeColor=colors.lightgrey, strokeWidth=0.5))
            
            # Draw Nodes
            for n in nodes:
                nx = (n["position"]["x"] - min_x + 20) * scale
                ny = 300 - (n["position"]["y"] - min_y + 20) * scale
                label = n.get("data", {}).get("label", n["id"])[:15]
                is_core = n.get("data", {}).get("category") == "CORE"
                
                # Box
                d.add(Rect(nx, ny - 15, 80 * scale, 30 * scale, 
                           fillColor=colors.lightblue if is_core else colors.lightgrey,
                           strokeColor=colors.darkblue if is_core else colors.grey))
                # Label
                d.add(String(nx + 5, ny - 5, label, fontSize=6, fontName='Helvetica'))
            
            elements.append(d)
        else:
            elements.append(Paragraph("No layout data available for visualization.", normal_style))
            
        elements.append(Spacer(1, 24))

        # --- SECTION 3: RISKS, GAPS & OBSERVATIONS ---
        elements.append(Paragraph("3. Observations & Strategic Risks", h2_style))

        
        # Gaps (Missing Assets)
        gaps = config.get("gaps", [])
        if gaps:
            elements.append(Paragraph("<b>[CRITICAL] Identified Gaps (Missing Assets):</b>", normal_style))
            for gap in gaps:
                elements.append(Paragraph(f"• {gap}", normal_style))
            elements.append(Spacer(1, 12))

        obs = config.get("triage_observations", [])
        if obs:
            elements.append(Paragraph("<b>Technical Observations:</b>", normal_style))
            for o in obs:
                elements.append(Paragraph(f"• {o}", normal_style))
        else:
            elements.append(Paragraph("No major technical risks detected during automated triage.", normal_style))
            
        questions = config.get("critical_questions", [])
        if questions:
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("<b>Critical Clarifications Required:</b>", normal_style))
            for q in questions:
                elements.append(Paragraph(f"? {q}", normal_style))
        
        elements.append(Spacer(1, 24))

        # --- SECTION 3: CRUD CROSS-REFERENCE MATRIX ---
        elements.append(Paragraph("3. CRUD Cross-Reference Matrix", h2_style))
        elements.append(Paragraph("Consolidated view of database IO and asset interactions.", normal_style))
        elements.append(Spacer(1, 12))
        
        table_ops = {} # {table_name: {"read": [], "write": []}}
        for asset in core_assets:
            meta = asset.get("metadata") or {}
            sources = meta.get("sources", [])
            targets = meta.get("targets", [])
            filename = asset.get("filename", "Unknown")
            
            for s in sources:
                table_ops.setdefault(s, {"read": [], "write": []})["read"].append(filename)
            for t in targets:
                table_ops.setdefault(t, {"read": [], "write": []})["write"].append(filename)
        
        if table_ops:
            crud_data = [["Database Table", "Read By (Sources)", "Written By (Targets)"]]
            for table, ops in sorted(table_ops.items()):
                reads = "\n".join(list(set(ops["read"])))
                writes = "\n".join(list(set(ops["write"])))
                crud_data.append([table, reads, writes])
            
            ct = Table(crud_data, colWidths=[150, 180, 180])
            ct.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(ct)
        else:
            elements.append(Paragraph("No explicit table IO detected for matrix generation.", normal_style))
            
        elements.append(Spacer(1, 24))
        
        # --- SECTION 4: DETAILED COMPONENT ANALYSIS ---
        elements.append(Paragraph("4. Detailed Component Analysis", h2_style))
        
        # Map dependencies for quick lookup
        upstream = {}
        downstream = {}
        edges = layout.get("edges", [])
        nodes = layout.get("nodes", [])
        # Create a map of ID to Name for readable dependencies
        id_to_name = {n["id"]: (n.get("data", {}).get("label") or n["id"]) for n in nodes}
        
        for edge in edges:
            src = edge.get("source")
            tgt = edge.get("target")
            if src and tgt:
                downstream.setdefault(src, []).append(id_to_name.get(tgt, tgt))
                upstream.setdefault(tgt, []).append(id_to_name.get(src, src))

        # Effort Mapping
        effort_map = {"LOW": "S (Small)", "MEDIUM": "M (Medium)", "HIGH": "L (Large)", "XHIGH": "XL (Extra Large)"}

        for asset in core_assets:
            asset_id = asset.get("id")
            filename = asset.get("filename", "Unknown")
            elements.append(Paragraph(f"Asset: {filename}", h3_style))
            
            meta = asset.get("metadata") or {}
            tech_sum = meta.get("technical_summary") or {}
            
            # Purpose & Effort
            complexity = tech_sum.get("complexity", "LOW").upper()
            effort = effort_map.get(complexity, "S (Small)")
            
            elements.append(Paragraph(f"<b>Purpose:</b> {tech_sum.get('purpose', 'N/A')}", normal_style))
            elements.append(Paragraph(f"<b>Complexity:</b> {complexity} | <b>Estimated Effort:</b> {effort}", normal_style))

            
            # Dependencies
            up = upstream.get(asset_id, [])
            down = downstream.get(asset_id, [])
            if up:
                elements.append(Paragraph(f"<b>Upstream (Dependencies):</b> {', '.join(up)}", normal_style))
            if down:
                elements.append(Paragraph(f"<b>Downstream (Consumers):</b> {', '.join(down)}", normal_style))
            
            # IO Summary
            inputs = ", ".join(tech_sum.get("inputs", []))
            outputs = ", ".join(tech_sum.get("outputs", []))
            if inputs: elements.append(Paragraph(f"<b>Source Inputs:</b> {inputs}", normal_style))
            if outputs: elements.append(Paragraph(f"<b>Target Outputs:</b> {outputs}", normal_style))
            
            # Steps
            steps = tech_sum.get("main_steps", [])
            if steps:
                elements.append(Paragraph("<b>Logic Flow:</b>", normal_style))
                for step in steps:
                    elements.append(Paragraph(f"• {step}", normal_style))
            
            # Code / Snippets
            if "logic_snippet" in meta:
                elements.append(Paragraph("<b>Key Logic Snippet:</b>", normal_style))
                snippet = meta["logic_snippet"]
                # Escape for XML
                snippet = snippet.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                elements.append(Paragraph(f"<pre>{snippet[:600]}...</pre>", code_style))
            
            # Driver-specific metadata
            if "sources" in meta and meta.get("sources"):
                 elements.append(Paragraph(f"<b>Detected Tables (IO):</b> {', '.join(meta['sources'][:5])} -> {', '.join(meta.get('targets', [])[:5])}", normal_style))

            elements.append(Spacer(1, 12))
            elements.append(Paragraph("-" * 100, normal_style))
            elements.append(Spacer(1, 12))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.read()

    @staticmethod
    def generate_final_report_pdf(report_data: Dict[str, Any]) -> bytes:
        """
        Generates a comprehensive Governance & Lineage PDF report for the Final Stage.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Custom Styles
        title_style = styles["Title"]
        h2_style = styles["Heading2"]
        h3_style = styles["Heading3"]
        normal_style = styles["Normal"]
        code_style = ParagraphStyle(
            'Code',
            parent=styles['Normal'],
            fontName='Courier',
            fontSize=7,
            leftIndent=20,
            spaceBefore=6,
            spaceAfter=6,
            backColor=colors.whitesmoke,
            borderPadding=5
        )

        project_name = report_data.get("name", "Unknown")
        gov_data = report_data.get("governance", {})
        stats = gov_data.get("stats", {})
        lineage = gov_data.get("lineage", [])

        # --- HEADER ---
        elements.append(Paragraph(f"Modernization Certificate: {project_name}", title_style))
        elements.append(Paragraph(f"Certified At: {gov_data.get('certified_at', 'N/A')}", normal_style))
        elements.append(Spacer(1, 24))

        # --- SECTION 1: EXECUTIVE SUMMARY ---
        elements.append(Paragraph("1. Executive Summary & Compliance Score", h2_style))
        
        score = gov_data.get("score", 0)
        score_color = "green" if score >= 90 else "orange"
        elements.append(Paragraph(f"<b>Architect Score:</b> <font color={score_color} size=14><b>{score}/100</b></font>", normal_style))
        elements.append(Spacer(1, 6))
        
        summary_text = f"The legacy solution has been successfully transformed into a modern Data Lakehouse architecture. {stats.get('total_files', 0)} files processed resulting in {stats.get('total_lines', 0)} lines of PySpark code."
        elements.append(Paragraph(summary_text, normal_style))
        elements.append(Spacer(1, 12))

        # Stats Table
        stat_data = [
            ["Metric", "Value"],
            ["Bronze Layer Files", str(stats.get("bronze_count", 0))],
            ["Silver Layer Files", str(stats.get("silver_count", 0))],
            ["Gold Layer Files", str(stats.get("gold_count", 0))],
            ["Total Refined Files", str(stats.get("total_files", 0))]
        ]
        t = Table(stat_data, colWidths=[200, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 24))

        # --- SECTION 2: MEDALLION LINEAGE ---
        elements.append(Paragraph("2. Medallion Architecture Lineage", h2_style))
        elements.append(Paragraph("Traceability from source assets to the Lakehouse layers.", normal_style))
        elements.append(Spacer(1, 12))

        lineage_data = [["Source Asset", "Bronze (Raw)", "Silver (Clean)", "Gold (Business)"]]
        for item in lineage:
            targets = item.get("targets", {})
            lineage_data.append([
                Paragraph(item.get("source", ""), normal_style),
                Paragraph(targets.get("bronze", "").split(".")[-1], normal_style),
                Paragraph(targets.get("silver", "").split(".")[-1], normal_style),
                Paragraph(targets.get("gold", "").split(".")[-1], normal_style)
            ])
        
        lt = Table(lineage_data, colWidths=[120, 100, 100, 100])
        lt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(lt)
        elements.append(Spacer(1, 24))

        # --- SECTION 3: COMPLIANCE AUDIT ---
        elements.append(Paragraph("3. Compliance Audit Trail", h2_style))
        logs = gov_data.get("compliance_logs", [])
        
        if logs:
            for log in logs:
                status = log.get("status", "INFO")
                color = "green" if status == "PASSED" else "black"
                msg = f"<font color={color}><b>[{status}]</b></font> {log.get('message', '')}"
                elements.append(Paragraph(msg, normal_style))
        else:
             elements.append(Paragraph("No specific audit logs found.", normal_style))

        elements.append(Spacer(1, 24))

        # --- SECTION 4: OPERATING MANUAL ---
        elements.append(Paragraph("4. AI Operating Manual", h2_style))
        elements.append(Paragraph("Technical context generated by the Shift-T Governance Agent.", normal_style))
        elements.append(Spacer(1, 12))
        
        import html
        manual_content = report_data.get("manual_content", "No manual content available.")
        # Escape HTML characters to prevent ReportLab XML parser errors
        safe_content = html.escape(manual_content).replace("\n", "<br/>")
        elements.append(Paragraph(safe_content[:10000], normal_style))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.read()




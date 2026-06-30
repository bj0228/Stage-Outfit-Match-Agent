import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class ReportGenerator:
    def __init__(self, reports_dir: str) -> None:
        self.reports_dir = reports_dir
        os.makedirs(self.reports_dir, exist_ok=True)
        self.font_name = self._register_font()

    def create(self, payload: dict, result: dict) -> tuple[str, str]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_id = f"stage_outfit_report_{timestamp}.pdf"
        path = os.path.join(self.reports_dir, report_id)

        doc = SimpleDocTemplate(
            path,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
        )
        styles = self._styles()
        story = [
            Paragraph("演出服搭配智能体报告", styles["Title"]),
            Paragraph("Stage Outfit Match Agent", styles["Subtitle"]),
            Spacer(1, 8),
        ]

        self._section(story, styles, "一、输入信息")
        story.append(Paragraph(f"舞蹈题目或链接：{self._escape(payload.get('dance_input', ''))}", styles["Body"]))
        story.append(Paragraph(f"目标风格：{self._escape(payload.get('style', ''))}", styles["Body"]))
        story.append(Paragraph(f"预算偏好：{self._escape(payload.get('budget', ''))}", styles["Body"]))

        self._section(story, styles, "二、舞蹈与风格分析")
        story.append(Paragraph(self._escape(result.get("dance_analysis", "")), styles["Body"]))
        story.append(Paragraph("关键词：" + "、".join(result.get("style_keywords", [])), styles["Body"]))

        self._section(story, styles, "三、参考来源")
        for index, source in enumerate(result.get("reference_sources", []), 1):
            story.append(Paragraph(f"{index}、{self._escape(source)}", styles["Body"]))

        self._section(story, styles, "四、五套搭配推荐")
        for index, outfit in enumerate(result.get("outfits", []), 1):
            story.append(Paragraph(f"{index}、{self._escape(outfit.get('name', ''))}", styles["H2"]))
            story.append(Paragraph(self._escape(outfit.get("concept", "")), styles["Body"]))
            story.append(Paragraph(f"参考：{self._escape(outfit.get('reference', ''))}", styles["Body"]))
            table_data = [["类别", "单品", "价格", "搜索链接"]]
            for item in outfit.get("items", []):
                links = item.get("links", {})
                table_data.append([
                    item.get("type", ""),
                    item.get("name", ""),
                    f"¥{item.get('price', 0)}",
                    " / ".join(links.keys()),
                ])
            table_data.append(["合计", "", f"¥{outfit.get('total_price', 0)}", ""])
            table = Table(table_data, colWidths=[28 * mm, 62 * mm, 24 * mm, 42 * mm])
            table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), self.font_name),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#101318")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d8d1c7")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fbf7f1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
            ]))
            story.append(table)
            story.append(Spacer(1, 8))

        self._section(story, styles, "五、试穿与舞台安全建议")
        for index, note in enumerate(result.get("styling_notes", []), 1):
            story.append(Paragraph(f"{index}、{self._escape(note)}", styles["Body"]))

        doc.build(story)
        return report_id, path

    def _section(self, story: list, styles: dict, title: str) -> None:
        story.append(Spacer(1, 10))
        story.append(Paragraph(title, styles["H1"]))
        story.append(Spacer(1, 4))

    def _register_font(self) -> str:
        try:
            pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
            return "STSong-Light"
        except Exception:
            return "Helvetica"

    def _styles(self) -> dict:
        styles = getSampleStyleSheet()
        return {
            "Title": ParagraphStyle(
                "Title",
                parent=styles["Title"],
                fontName=self.font_name,
                fontSize=23,
                leading=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#101318"),
            ),
            "Subtitle": ParagraphStyle(
                "Subtitle",
                parent=styles["BodyText"],
                fontName=self.font_name,
                fontSize=10,
                leading=16,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#9b5d31"),
            ),
            "H1": ParagraphStyle(
                "H1",
                parent=styles["Heading1"],
                fontName=self.font_name,
                fontSize=15,
                leading=22,
                textColor=colors.HexColor("#9b3d2e"),
            ),
            "H2": ParagraphStyle(
                "H2",
                parent=styles["Heading2"],
                fontName=self.font_name,
                fontSize=12.5,
                leading=18,
                textColor=colors.HexColor("#101318"),
            ),
            "Body": ParagraphStyle(
                "Body",
                parent=styles["BodyText"],
                fontName=self.font_name,
                fontSize=10.5,
                leading=17,
                textColor=colors.HexColor("#2d2a26"),
                spaceAfter=5,
            ),
        }

    def _escape(self, value: str) -> str:
        return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

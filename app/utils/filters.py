"""Jinja2 自訂 filter"""
import markdown
from flask import Flask
from markupsafe import Markup


def register_filters(app: Flask) -> None:
    @app.template_filter("markdown")
    def render_markdown(text: str) -> Markup:
        """將 Markdown 轉為安全的 HTML"""
        import bleach

        html = markdown.markdown(
            text or "",
            extensions=["extra", "codehilite", "toc", "nl2br"],
        )
        allowed_tags = [
            "p", "br", "strong", "em", "a", "ul", "ol", "li",
            "h1", "h2", "h3", "h4", "h5", "h6", "blockquote",
            "code", "pre", "img", "table", "thead", "tbody", "tr", "th", "td",
            "hr", "del", "ins",
        ]
        allowed_attrs = {
            "a": ["href", "title", "target", "rel"],
            "img": ["src", "alt", "title", "width", "height"],
            "*": ["class", "id"],
        }
        clean = bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs)
        return Markup(clean)

    @app.template_filter("date_tw")
    def format_date_tw(dt) -> str:
        """格式化為台灣日期格式 2026年5月17日"""
        if not dt:
            return ""
        return dt.strftime("%Y年%m月%d日")

    @app.template_filter("datetime_tw")
    def format_datetime_tw(dt) -> str:
        if not dt:
            return ""
        return dt.strftime("%Y/%m/%d %H:%M")

    @app.template_filter("filesize")
    def format_filesize(size: int) -> str:
        if not size:
            return "0 B"
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @app.template_filter("truncate_chars")
    def truncate_chars(text: str, length: int = 100) -> str:
        if not text:
            return ""
        return text[:length] + "…" if len(text) > length else text

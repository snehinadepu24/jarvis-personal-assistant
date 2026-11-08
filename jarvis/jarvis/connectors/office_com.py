from __future__ import annotations

import sys
from typing import Any

if sys.platform != "win32":
    def excel_set_cell(sheet_name: str, cell: str, value: Any) -> dict:
        return {"ok": False, "detail": "Office COM is Windows-only"}

    def outlook_create_draft(to: str, subject: str, body: str) -> dict:
        return {"ok": False, "detail": "Office COM is Windows-only"}

    def outlook_send(to: str, subject: str, body: str) -> dict:
        return {"ok": False, "detail": "Office COM is Windows-only"}
else:
    import win32com.client

    def excel_set_cell(sheet_name: str, cell: str, value: Any) -> dict:
        try:
            excel = win32com.client.Dispatch("Excel.Application")
            wb = excel.ActiveWorkbook
            if not wb:
                return {"ok": False, "detail": "No active Excel workbook"}
            ws = wb.Sheets(sheet_name) if sheet_name else wb.ActiveSheet
            ws.Range(cell).Value = value
            return {"ok": True, "detail": f"Set {cell} in {sheet_name or 'ActiveSheet'} to {value}"}
        except Exception as e:
            return {"ok": False, "detail": str(e)}

    def outlook_create_draft(to: str, subject: str, body: str) -> dict:
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            mail = outlook.CreateItem(0)
            mail.To = to
            mail.Subject = subject
            mail.Body = body
            mail.Save()
            return {"ok": True, "detail": f"Draft created for {to}"}
        except Exception as e:
            return {"ok": False, "detail": str(e)}

    def outlook_send(to: str, subject: str, body: str) -> dict:
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            mail = outlook.CreateItem(0)
            mail.To = to
            mail.Subject = subject
            mail.Body = body
            mail.Send()
            return {"ok": True, "detail": f"Mail sent to {to}"}
        except Exception as e:
            return {"ok": False, "detail": str(e)}

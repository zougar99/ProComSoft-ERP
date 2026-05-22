# -*- coding: utf-8 -*-
"""
نماذج الفواتير القابلة للتخصيص (مشابهة لـ Free Devis Factures 2)
"""
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from config.settings import BASE_DIR

TEMPLATES_DIR = BASE_DIR / "templates"


class InvoiceTemplate:
    """نموذج فاتورة قابل للتخصيص"""
    
    def __init__(self, template_name="default"):
        self.template_name = template_name
        self.template_path = TEMPLATES_DIR / f"{template_name}.xml"
        self.template_dir = TEMPLATES_DIR
        self.template_dir.mkdir(exist_ok=True)
        
    def load_template(self):
        """تحميل النموذج من ملف XML"""
        if not self.template_path.exists():
            self.create_default_template()
            
        tree = ET.parse(self.template_path)
        return tree.getroot()
        
    def create_default_template(self):
        """إنشاء نموذج افتراضي"""
        root = ET.Element("InvoiceTemplate")
        root.set("version", "1.0")
        
        # رأس الفاتورة
        header = ET.SubElement(root, "Header")
        ET.SubElement(header, "Logo").set("position", "left")
        ET.SubElement(header, "CompanyName").text = "[CompanyName]"
        ET.SubElement(header, "CompanyAddress").text = "[CompanyAddress]"
        ET.SubElement(header, "CompanyPhone").text = "[CompanyPhone]"
        ET.SubElement(header, "CompanyEmail").text = "[CompanyEmail]"
        
        # معلومات العميل
        customer = ET.SubElement(root, "Customer")
        ET.SubElement(customer, "Name").text = "[CustomerName]"
        ET.SubElement(customer, "Address").text = "[CustomerAddress]"
        ET.SubElement(customer, "TaxID").text = "[CustomerTaxID]"
        
        # معلومات الفاتورة
        invoice_info = ET.SubElement(root, "InvoiceInfo")
        ET.SubElement(invoice_info, "Number").text = "[InvoiceNumber]"
        ET.SubElement(invoice_info, "Date").text = "[InvoiceDate]"
        ET.SubElement(invoice_info, "DueDate").text = "[DueDate]"
        
        # جدول العناصر
        items = ET.SubElement(root, "Items")
        item = ET.SubElement(items, "Item")
        ET.SubElement(item, "Description").text = "[ItemDescription]"
        ET.SubElement(item, "Quantity").text = "[ItemQuantity]"
        ET.SubElement(item, "UnitPrice").text = "[ItemUnitPrice]"
        ET.SubElement(item, "Total").text = "[ItemTotal]"
        
        # الإجماليات
        totals = ET.SubElement(root, "Totals")
        ET.SubElement(totals, "Subtotal").text = "[Subtotal]"
        ET.SubElement(totals, "Tax").text = "[Tax]"
        ET.SubElement(totals, "Total").text = "[Total]"
        
        # التذييل
        footer = ET.SubElement(root, "Footer")
        ET.SubElement(footer, "Notes").text = "[Notes]"
        ET.SubElement(footer, "PaymentTerms").text = "[PaymentTerms]"
        
        # حفظ النموذج
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(self.template_path, encoding='utf-8', xml_declaration=True)
        
    def render(self, invoice_data):
        """تطبيق البيانات على النموذج"""
        template = self.load_template()
        
        # استبدال المتغيرات بالبيانات الفعلية
        replacements = {
            "[CompanyName]": invoice_data.get("company_name", ""),
            "[CompanyAddress]": invoice_data.get("company_address", ""),
            "[CompanyPhone]": invoice_data.get("company_phone", ""),
            "[CompanyEmail]": invoice_data.get("company_email", ""),
            "[CustomerName]": invoice_data.get("customer_name", ""),
            "[CustomerAddress]": invoice_data.get("customer_address", ""),
            "[CustomerTaxID]": invoice_data.get("customer_tax_id", ""),
            "[InvoiceNumber]": invoice_data.get("invoice_number", ""),
            "[InvoiceDate]": invoice_data.get("invoice_date", ""),
            "[DueDate]": invoice_data.get("due_date", ""),
            "[Subtotal]": f"{invoice_data.get('subtotal', 0):.2f}",
            "[Tax]": f"{invoice_data.get('tax', 0):.2f}",
            "[Total]": f"{invoice_data.get('total', 0):.2f}",
            "[Notes]": invoice_data.get("notes", ""),
            "[PaymentTerms]": invoice_data.get("payment_terms", ""),
        }
        
        # استبدال في النص
        def replace_text(element):
            if element.text:
                for old, new in replacements.items():
                    element.text = element.text.replace(old, new)
            for child in element:
                replace_text(child)
                
        replace_text(template)
        
        return template
        
    def save_template(self, template_xml):
        """حفظ النموذج"""
        tree = ET.ElementTree(template_xml)
        ET.indent(tree, space="  ")
        tree.write(self.template_path, encoding='utf-8', xml_declaration=True)


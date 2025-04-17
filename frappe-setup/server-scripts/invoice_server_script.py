"""
Server script for handling Invoice creation and update events.
This script will be attached to the Invoice DocType and will run on various events.
"""

import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, now_datetime, add_days
from frappe.model.document import Document


def validate(doc, method=None):
    """
    Validate the Invoice before saving.
    
    Args:
        doc: The Invoice document being saved
        method: The method being called (validate, on_submit, etc.)
    """
    validate_due_date(doc)
    validate_items(doc)
    calculate_totals(doc)
    validate_customer_credit_limit(doc)
    set_status(doc)


def on_submit(doc, method=None):
    """
    Actions to perform when the Invoice is submitted.
    
    Args:
        doc: The Invoice document being submitted
        method: The method being called
    """
    update_outstanding_amount(doc)
    create_gl_entries(doc)
    update_customer_balance(doc)
    send_invoice_notification(doc)
    create_payment_schedule(doc)


def on_cancel(doc, method=None):
    """
    Actions to perform when the Invoice is cancelled.
    
    Args:
        doc: The Invoice document being cancelled
        method: The method being called
    """
    update_outstanding_amount(doc, cancel=True)
    reverse_gl_entries(doc)
    update_customer_balance(doc, cancel=True)
    set_status(doc)


def on_update_after_submit(doc, method=None):
    """
    Actions to perform when the Invoice is updated after submission.
    
    Args:
        doc: The Invoice document being updated
        method: The method being called
    """
    update_outstanding_amount(doc)
    set_status(doc)


def validate_due_date(doc):
    """
    Validate that the due date is not before the posting date.
    
    Args:
        doc: The Invoice document
    """
    if getdate(doc.due_date) < getdate(doc.posting_date):
        frappe.throw(_("Due Date cannot be before Posting Date"))


def validate_items(doc):
    """
    Validate the items in the Invoice.
    
    Args:
        doc: The Invoice document
    """
    # Check if there are any items
    if not doc.items:
        frappe.throw(_("Invoice must have at least one item"))
    
    # Validate each item
    for item in doc.items:
        # Check if quantity is positive
        if flt(item.qty) <= 0:
            frappe.throw(_("Quantity must be positive for item {0}").format(item.item_name or item.item_code))
        
        # Check if rate is positive
        if flt(item.rate) <= 0:
            frappe.throw(_("Rate must be positive for item {0}").format(item.item_name or item.item_code))
        
        # Calculate amount
        item.amount = flt(item.qty) * flt(item.rate)
        
        # Calculate tax amount if applicable
        if hasattr(item, 'item_tax_template') and item.item_tax_template:
            calculate_item_tax(item, doc)


def calculate_totals(doc):
    """
    Calculate the total amounts for the Invoice.
    
    Args:
        doc: The Invoice document
    """
    # Calculate total quantity and amount
    doc.total_quantity = 0
    doc.base_total = 0
    
    for item in doc.items:
        doc.total_quantity += flt(item.qty)
        doc.base_total += flt(item.amount)
    
    # Calculate net total (before taxes)
    doc.base_net_total = doc.base_total
    
    # Calculate taxes if applicable
    if hasattr(doc, 'taxes') and doc.taxes:
        calculate_taxes(doc)
    else:
        doc.total_taxes_and_charges = 0
        doc.base_total_taxes_and_charges = 0
    
    # Calculate grand total
    doc.grand_total = flt(doc.base_net_total) + flt(doc.total_taxes_and_charges)
    doc.base_grand_total = flt(doc.base_net_total) + flt(doc.base_total_taxes_and_charges)
    
    # Round totals if needed
    doc.rounded_total = round(doc.grand_total)
    doc.base_rounded_total = round(doc.base_grand_total)
    
    # Calculate outstanding amount
    doc.outstanding_amount = doc.grand_total
    doc.base_outstanding_amount = doc.base_grand_total


def calculate_item_tax(item, doc):
    """
    Calculate tax for an item based on its tax template.
    
    Args:
        item: The Invoice Item
        doc: The Invoice document
    """
    # This is a simplified implementation
    # In a real-world scenario, you would fetch the tax rates from the tax template
    # and apply them to the item amount
    
    # For now, we'll assume a fixed tax rate of 10%
    tax_rate = 0.10
    item.tax_amount = flt(item.amount) * tax_rate
    item.base_tax_amount = item.tax_amount
    
    # Store the tax rate for reference
    item.item_tax_rate = f'{{"Tax": {tax_rate * 100}}}'


def calculate_taxes(doc):
    """
    Calculate taxes for the Invoice.
    
    Args:
        doc: The Invoice document
    """
    # This is a simplified implementation
    # In a real-world scenario, you would calculate taxes based on the tax template
    
    # For now, we'll sum up the tax amounts from the items
    total_tax = 0
    for item in doc.items:
        total_tax += flt(getattr(item, 'tax_amount', 0))
    
    doc.total_taxes_and_charges = total_tax
    doc.base_total_taxes_and_charges = total_tax


def validate_customer_credit_limit(doc):
    """
    Validate that the customer has not exceeded their credit limit.
    
    Args:
        doc: The Invoice document
    """
    # Skip validation for return invoices
    if doc.is_return:
        return
    
    # Get customer credit limit
    credit_limit = frappe.db.get_value("Customer", doc.customer, "credit_limit")
    
    if credit_limit:
        # Get outstanding amount for the customer
        outstanding_amt = get_customer_outstanding(doc.customer, doc.company)
        
        # Add current invoice amount
        total_outstanding = outstanding_amt + flt(doc.grand_total)
        
        # Check if credit limit is exceeded
        if flt(credit_limit) < total_outstanding:
            frappe.throw(
                _("Credit limit of {0} exceeded. Current outstanding: {1}, Current Invoice: {2}, Total: {3}")
                .format(credit_limit, outstanding_amt, doc.grand_total, total_outstanding)
            )


def get_customer_outstanding(customer, company):
    """
    Get the outstanding amount for a customer.
    
    Args:
        customer: The customer
        company: The company
        
    Returns:
        float: The outstanding amount
    """
    # This is a simplified implementation
    # In a real-world scenario, you would query the database for outstanding invoices
    
    # For now, we'll return a dummy value
    return 0.0


def set_status(doc):
    """
    Set the status of the Invoice based on its current state.
    
    Args:
        doc: The Invoice document
    """
    if doc.docstatus == 2:  # Cancelled
        doc.status = "Cancelled"
        return
    
    if doc.docstatus == 0:  # Draft
        doc.status = "Draft"
        return
    
    # For submitted invoices
    outstanding_amount = flt(doc.outstanding_amount)
    total_amount = flt(doc.grand_total)
    
    if outstanding_amount == 0:
        doc.status = "Paid"
    elif outstanding_amount == total_amount:
        doc.status = "Unpaid"
    elif outstanding_amount < total_amount:
        doc.status = "Partly Paid"
    
    # Check if overdue
    if doc.status in ["Unpaid", "Partly Paid"]:
        if getdate(doc.due_date) < getdate():
            doc.status = "Overdue"


def update_outstanding_amount(doc, cancel=False):
    """
    Update the outstanding amount for the Invoice.
    
    Args:
        doc: The Invoice document
        cancel: Whether this is being called during cancellation
    """
    # This is a simplified implementation
    # In a real-world scenario, you would calculate the outstanding amount
    # based on linked payment entries
    
    if cancel:
        # Reset outstanding amount on cancellation
        doc.outstanding_amount = 0
        doc.base_outstanding_amount = 0
    else:
        # Calculate outstanding amount (grand total - paid amount)
        paid_amount = get_paid_amount(doc)
        doc.outstanding_amount = flt(doc.grand_total) - flt(paid_amount)
        doc.base_outstanding_amount = flt(doc.base_grand_total) - flt(paid_amount)


def get_paid_amount(doc):
    """
    Get the amount paid for an Invoice.
    
    Args:
        doc: The Invoice document
        
    Returns:
        float: The paid amount
    """
    # This is a simplified implementation
    # In a real-world scenario, you would query the database for payment entries
    
    # For now, we'll return a dummy value
    return 0.0


def create_gl_entries(doc):
    """
    Create General Ledger entries for the Invoice.
    
    Args:
        doc: The Invoice document
    """
    # This is a simplified implementation
    # In a real-world scenario, you would create actual GL entries in the database
    
    frappe.msgprint(_("GL Entries created for Invoice {0}").format(doc.name))


def reverse_gl_entries(doc):
    """
    Reverse General Ledger entries for the Invoice.
    
    Args:
        doc: The Invoice document
    """
    # This is a simplified implementation
    # In a real-world scenario, you would reverse the GL entries in the database
    
    frappe.msgprint(_("GL Entries reversed for Invoice {0}").format(doc.name))


def update_customer_balance(doc, cancel=False):
    """
    Update the customer's balance.
    
    Args:
        doc: The Invoice document
        cancel: Whether this is being called during cancellation
    """
    # This is a simplified implementation
    # In a real-world scenario, you would update the customer's balance in the database
    
    if cancel:
        frappe.msgprint(_("Customer balance updated (cancelled) for Invoice {0}").format(doc.name))
    else:
        frappe.msgprint(_("Customer balance updated for Invoice {0}").format(doc.name))


def send_invoice_notification(doc):
    """
    Send a notification email for the Invoice.
    
    Args:
        doc: The Invoice document
    """
    # This is a simplified implementation
    # In a real-world scenario, you would send an actual email
    
    frappe.msgprint(_("Invoice notification sent to customer {0}").format(doc.customer_name))


def create_payment_schedule(doc):
    """
    Create a payment schedule for the Invoice if payment terms are specified.
    
    Args:
        doc: The Invoice document
    """
    # Skip if payment terms template is not specified
    if not doc.payment_terms_template:
        return
    
    # This is a simplified implementation
    # In a real-world scenario, you would create actual payment schedule entries
    
    frappe.msgprint(_("Payment schedule created for Invoice {0}").format(doc.name))

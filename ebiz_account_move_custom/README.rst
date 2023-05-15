
eBiz Accounting Customized
-------------------------------------
This module adds custom fields and logic to the accounting application.
To view the customizations, please refer to the following:

1. APE-41: Journal Entries and Credit Notes
--------------------------------------------
Look at [15-65](./models/account.py)
Added an additional column to display the check number for paid invoices in the accounting move record.
->
The payment check number is computed based on the payment data of the accounting move record.
If the payment method is 'Checks', the check number is extracted and assigned to the payment_check_number
field of the accounting move record.
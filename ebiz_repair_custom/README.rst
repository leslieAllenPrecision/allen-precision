
eBiz Repair Customized
-------------------------------------
This module adds custom fields and logic to the repair application.
To view the customizations, please refer to the following:

1. APE-37: Changes to the Repair Orders entry screen
--------------------------------------------
Look at [9](./models/repair.py) and Look at [5-31](./views/repair.xml)
A new, open text field called “Production Information” is added under it, where users can type the product’s information.

Look at [3-9](./report/repair_report.xml)
“Production Information” field is also be added to the repair report.
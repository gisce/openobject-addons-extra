{
    "name" : "CCI Salesman",
    "version" : "1.0",
    "author" : "PCSOL",
    "category" : "Profile",
    "website": "http://www.pcsol.be",
    "description": """CCI Salesman""",
    "depends" : ['base', 'cci_last_module', 'base_contact'],
    "update_xml" : ['wizard/partner_interest_order.xml',
                    'partner_view.xml',
                    'users_view.xml',
                    'wizard/partner_interest_next.xml',
                    'crm_data.xml',
                    'script.sql'],
    "active": False,
    "installable": True
}

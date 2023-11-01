# Copyright 2017 ACSONE SA/NV
# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "COVAGRO Account Analytic Sequence",
    "summary": """
        Restore the analytic account sequence""",
    "version": "15.0.1.0.1",
    "license": "AGPL-3",
    "author": "Fall lewis YOMBA (OCA)",
    "depends": [
        "analytic",
    ],
    "data": [
        "data/sequence.xml",
    ],
    "post_init_hook": "post_init_hook",
}

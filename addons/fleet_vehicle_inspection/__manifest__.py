# Copyright 2020 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Inspection de véhicule COVAGRO",
    "summary": """
        This module extends the Fleet module allowing the registration
        of vehicle entry and exit inspections.""",
    "version": "15.0.1.0.0",
    "author": "Fall Lewis (OCA)",
    "maintainers": ["Fall Lewis"],
    "depends": ["fleet"],
    "data": [
        "security/fleet_vehicle_inspection_line_image.xml",
        "views/fleet_vehicle.xml",
        "security/fleet_vehicle_inspection_line.xml",
        "views/fleet_vehicle_inspection_line.xml",
        "security/fleet_vehicle_inspection_item.xml",
        "views/fleet_vehicle_inspection_item.xml",
        "security/fleet_vehicle_inspection.xml",
        "views/fleet_vehicle_inspection.xml",
        "data/fleet_vehicle_inspection.xml",
    ],
    "demo": ["demo/fleet_vehicle_inspection.xml"],
}

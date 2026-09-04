
COLUMN_MAPPINGS = {
    "mpdm": {
        "source_sheet": "mpdm",
        "destination_sheet": "MPDM",
        "source_start_row": 8,
        "dest_start_row": 13,

        "source_header_mappings": {
            "date": "J6",
            "project_code": "B6",
            "operation": "B8",
            "equipment_types": "E7",
            'equipment': "F7",
        },
        "dest_header_mappings": {
            "date": "G6",
            "project_code": "B6",
            "operation": "B8",
            "equipment_types": 'D9',
            'equipment': "B9"
        },
        "column_mappings": {

        }
    },
    
    "truck": {
        "source_sheet": "truck",
        "destination_sheet": "Truck",
        "source_start_row": 7,
        "dest_start_row": 11,

        "header_mappings": {
            "date": "A7",
            "project_code": "B7",
            "data_collector": "C7",
            "equipment_types": "D7",
        },

        "source_header_mappings": {
            "date": "A7",
            "project_code": "B7",
            "operation": "E7",
            "equipment_types": "A5",
            'equipment': "F7",
        },
        
        "dest_header_mappings": {
            "date": "M6",
            "project_code": "C6",
            "operation":"B8" ,
            "equipment_types": 'J6',
            'equipment': "B9"
        },
        
        "column_mappings": {
            "E": "B",  # Equipment Tag
            "F": "C",  # Man power
            "G": "D",  # Truck Plate or Tag
            "H": "E",  # Task Type
            "I": "F",  # Description
            "J": "G",  # Soil Type
            "P": "L",  # Unit
            "O": "N",  # Total Cycle Time
            "Q": "M",  # Q Actual Bucket capacity
        }
    },

    "dozer": {
        "source_sheet": "dozer",
        "destination_sheet": "Dozer",

        "source_start_row": 8,
        "dest_start_row": 11,

        "header_mappings": {
            "date": "L4",
            "project_code": "B4",
            "data_collector": "C4",
            "number_of_equipment_types": "I4",
        },

        "source_header_mappings": {
            "date": "L4",
            "project_code": "B4",
            "operation": "",
            "equipment_types": "I4",
            'equipment': "",
        },
        "dest_header_mappings": {
            "date": "L6",
            "project_code": "C6",
            "operation": None,
            "equipment_types": 'I6',
            'equipment': ""
        },


        "column_mappings": {
            'A': 'B',  # Equipment Tag (Dozer Cyle)
            'B': 'C',  # Man power
            'C': 'D',  # Dozer Blade Type
            'D': 'E',  # Task Type
            'E': 'F',  # Description
            'F': 'G',  # Soil Type
            'G': 'H',  # Blade Height (m)
            'H': 'I',  # Blade Width (m)
            'I': 'J',  # Blade Length (m)
            'J': 'K',  # unit (m3, m, etc)
            #'O': 'L',  # Blade Load (m3, m, etc) - This will be calculated, so we can skip copying this column
            'L': 'M',  # Cycle Time (seconds)
            # 'Q': 'N',
        },
        "custom_fields": {
            "blade_load":"K",

            "unit": "J",
        }
    },

    "excavator": {
        "source_sheet": "excavator",
        "destination_sheet": "Excavator",
        "source_start_row": 7,
        "dest_start_row": 11,

        "header_mappings": {
            "date": "A7",
            "project_code": "B7",
            "data_collector": "C7",
            "equipment_types": "D7",
        },

        "source_header_mappings": {
            "date": "A7",
            "project_code": "B7",
            "data_collector": "C7",
            "equipment_types": "D7",
        },

        "dest_header_mappings": {
            "date": "M6",
            "project_code": "C6",
            "equipment_types": "J6",
            "equipment": "B9",
            "operation": "B8",
        },

        "column_mappings": {
            'E': 'B',  # Equipment Tag (Dozer Cyle)
            'F': 'C',  # Man power
            'G': 'D',  # Dozer Blade Type
            'H': 'E',  # Task Type
            'I': 'F',  # Description
            'J': 'G',  # Soil Type
            'K': 'H',  # Bucket Fill factor
            'L': 'I',  # Angle of swing
            # 'M': 'I',  # Depth of Cut
            'N': 'J',   # Volume Correction
            'O': 'K',  # Efficiency (60m/60m)
            'P': 'L',  # unit (m3, m, etc)
            'Q': 'M',  # Q Heaped Bucket capacity(m3, m, etc) - 
            'R': 'N',  # Cycle Time (seconds)
        },

        "custom_columns": [
            "H","I", "J", "K"
        ],
        "custom_fields": {
            "swing_ratio": {
                "source_angle_col": "L",
                "source_depth_col": "M",
                "dest_col": "I"
            },

            "volume_correction": {
                "soil_type_col": "G",
                "dest_col": "J"
            },

            "efficiency": {
                "default": 60,
                "dest_col": "K"
            },
            "asd": {
                "default": 1.0,
                "dest_col": "I",
            },
            "fill_factor": {
                "defalt": 1.0,
                "dst_col": "H"
            },
            
        }
    }
}


COLUMN_MAPPINGS = {
    "truck": {
        "equipment_sheet": "truck",
        "mpdm_sheet": "mpdm",
        "equipment_start_row": 11,
        "mpdm_start_row": 13,

        "header_mappings": {
            "date": "L5",
            "project_code": "D6",
            "data_collector": "C7",
            "number_of_equipment_types": "I6",
        },
        

        "column_mappings": {
            "equipment": "M",
            "mpdm": "B",
        }

    },

    "dozer": {
        "equipment_sheet": "Dozer",
        "mpdm_sheet": "mpdm",
        "equipment_start_row": 11,
        "mpdm_start_row": 13,

        "header_mappings": {
            "date": "L5",
            "project_code": "D6",
            "data_collector": "C7",
            "number_of_equipment_types": "I6",
        },
        

        "column_mappings": {
            "equipment": "M",
            "mpdm": "B",
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
            "number_of_equipment_types": "D7",
        },


        "column_mappings": {
            'E': 'B',  # Equipment Tag (Dozer Cyle)
            'F': 'C',  # Man power
            'G': 'D',  # Dozer Blade Type
            'H': 'E',  # Task Type
            'I': 'F',  # Description
            'J': 'G',  # Soil Type
            'K': 'H',  # Bucket Fill factor
            #'L': 'I',  # Angle of swing
            #'M': 'I',  # Depth of Cut
            'N': 'J',   # Volume Correction
            'O': 'K',  # Efficiency (60m/60m)
            'P': 'L',  # unit (m3, m, etc)
            'Q': 'M',  # Q Heaped Bucket capacity(m3, m, etc) - 
            'R': 'N',  # Cycle Time (seconds)
        },
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
            }
        }
    }
}

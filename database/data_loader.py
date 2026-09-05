import json


class DataLoader:
    def __init__(self, data_file):
        self.data_file = data_file
        self.data = self._load_data()

    # def _load_data(self):
    #     with open(self.data_file, 'r') as f:
    #         data = json.load(f)

    #     print(f"Loaded data from {self.data_file}: {len(data)} entries")
    #     return data

    def _load_data(self):
        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Strip extra whitespace from all string fields
        cleaned_data = []
        for row in data:
            cleaned_row = {}
            for key, value in row.items():
                cleaned_row[key] = value.strip() if isinstance(value, str) else value
            cleaned_data.append(cleaned_row)

        # print(f"Loaded data from {self.data_file}: {len(cleaned_data)} entries")
        return cleaned_data

    def get_divisions(self, subsector):
        divs = set()
        for row in self.data:
            if row['subsector'] == subsector and 'division' in row:
                divs.add(str(row['division']))  # Convert int to str

        # print(f"Divisions for subsector '{subsector}': {divs}")
        # Sort numerically by converting back to int temporarily in key
        return sorted(list(divs), key=lambda x: int(x) if x.isdigit() else x)


    def get_tasks(self, subsector, division):
        tasks = set()
        for row in self.data    :
            if row['subsector'] == subsector and str(row['division']) == division:
                tasks.add(row['task'])
        # print(f"Tasks for subsector '{subsector}' and division '{division}': {tasks}")
        return sorted(list(tasks), key=lambda x: (int(x) if x.isdigit() else x))  # Sort numerically if possible

    def get_elements(self, subsector, division, task):
        elements = set()
        for row in self.data:
            if row['subsector'] == subsector and str(row['division']) == division and row['task'] == task:
                elements.add(row['element'])
        # print(f"Elements for subsector '{subsector}', division '{division}', and task '{task}': {elements}")
        return sorted(list(elements), key=lambda x: (int(x) if x.isdigit() else x))  # Sort numerically if possible

    def get_particulars(self, subsector, division, task, element):
        particulars = set()
        for row in self.data:
            if (row['subsector'] == subsector and str(row['division']) == division and row['task'] == task and row['element'] == element):
                # particulars.add(row['particular'])
                particular = f"{row['PID']} - {row['task']}-{row['element']}-{row['particular']}"
                particulars.add(particular)

        # print(f"Particulars for subsector '{subsector}', division '{division}', task '{task}', and element '{element}': {particulars}")
        return sorted(list(particulars), key=lambda x: (int(x) if x.isdigit() else x))  # Sort numerically if possible

    def get_all_particulars(self):
        particulars = set()
        for row in self.data:
            particular = f"{row['PID']} - {row['task']}-{row['element']}-{row['particular']}"
            particulars.add(particular)
        return sorted(list(particulars), key=lambda x: (int(x) if x.isdigit() else x))  # Sort numerically if possible

    def get_equipment(self, subsector, division, task, element, particular):
        equipment = set()
        for row in self.data:
            if (row['subsector'] == subsector and str(row['division']) == division and row['task'] == task and row['element'] == element and row['particular'] == particular):
                equipment.add(row['equipment'])
        print(f"Equipment for subsector '{subsector}', division '{division}', task '{task}', element '{element}', and particular '{particular}': {equipment}")
        return sorted(list(equipment))

    
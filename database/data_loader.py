import json


class DataLoader:
    def __init__(self, data_file):
        self.data_file = data_file
        self.data = self._load_data()

    def _load_data(self):
        with open(self.data_file, 'r') as f:
            data = json.load(f)

        print(f"Loaded data from {self.data_file}: {len(data)} entries")
        return data

    def get_divisions(self, subsector):
        divs = set()
        for row in self.data:
            if row['subsector'] == subsector:
                divs.add(row['division'])

        print(f"Divisions for subsector '{subsector}': {divs}")
        return sorted(list(divs))

    def get_tasks(self, subsector, division):
        tasks = set()
        for row in self.data    :
            if row['subsector'] == subsector and row['division'] == division:
                tasks.add(row['task'])
        print(f"Tasks for subsector '{subsector}' and division '{division}': {tasks}")
        return sorted(list(tasks))

    def get_elements(self, subsector, division, task):
        elements = set()
        for row in self.data:
            if row['subsector'] == subsector and row['division'] == division and row['task'] == task:
                elements.add(row['element'])
        print(f"Elements for subsector '{subsector}', division '{division}', and task '{task}': {elements}")
        return sorted(list(elements))

    def get_particulars(self, subsector, division, task, element):
        particulars = set()
        for row in self.data:
            if (row['subsector'] == subsector and row['division'] == division and
                    row['task'] == task and row['element'] == element):
                particulars.add(row['particular'])
        print(f"Particulars for subsector '{subsector}', division '{division}', task '{task}', and element '{element}': {particulars}")
        return sorted(list(particulars))

    def get_equipment(self, subsector, division, task, element, particular):
        equipment = set()
        for row in self.data:
            if (row['subsector'] == subsector and row['division'] == division and
                    row['task'] == task and row['element'] == element and
                    row['particular'] == particular):
                equipment.add(row['equipment'])
        print(f"Equipment for subsector '{subsector}', division '{division}', task '{task}', element '{element}', and particular '{particular}': {equipment}")
        return sorted(list(equipment))

    
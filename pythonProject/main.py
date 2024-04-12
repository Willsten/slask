import pandas as pd
class Cell:
    def __init__(self, number, voltage, ir, capacity):
        self.number = number
        self.voltage = voltage
        self.ir = ir
        self.capacity = capacity
class CellPair:
    def __init__(self, cell1, cell2):
        self.pair_number = None
        self.cell1 = cell1
        self.cell2 = cell2
        self.similarity_score = self.calculate_similarity()
        self.total_capacity = self.calculate_total_capacity()
        self.total_resistance = self.calculate_total_resistance()
        self.total_voltage = self.calculate_total_voltage()
        self.voltage_difference = abs(self.cell1.voltage - self.cell2.voltage)
        self.ir_difference = abs(self.cell1.ir - self.cell2.ir)
        self.capacity_difference = abs(self.cell1.capacity - self.cell2.capacity)
    def calculate_similarity(self):
        voltage_diff = abs(self.cell1.voltage - self.cell2.voltage)
        resistance_diff = abs(self.cell1.ir - self.cell2.ir)
        capacity_diff = abs(self.cell1.capacity - self.cell2.capacity)
        return voltage_diff + resistance_diff + capacity_diff

    def calculate_total_capacity(self):
        if self.cell1 and self.cell2 is not None:
            total = self.cell1.capacity + self.cell2.capacity
        return total

    def calculate_total_resistance(self):
        if self.cell1 and self.cell2 is not None:
            total = 1 / ((1 / self.cell1.ir) + (1 / self.cell2.ir))
        return total

    def calculate_total_voltage(self):
        if self.cell1.voltage < self.cell2.voltage:
            total_voltage = self.cell1.voltage
        else:
            total_voltage = self.cell2.voltage
        return total_voltage

class Segment:
    def __init__(self, cell_pairs):
        self.cell_pairs = cell_pairs
        self.segment_total_resistance = self.calculate_segment_total_resistance()
        self.segment_total_capacity = self.calculate_segment_total_capacity()
        self.average_ir_difference = self.calculate_average_ir_difference()
        self.max_voltage_difference = self.calculate_max_voltage_difference()
    def calculate_segment_total_capacity(self):
        capacity = float("inf")
        for pair in self.cell_pairs:
            if pair.total_capacity < capacity:
                capacity = pair.total_capacity
            else:
                continue
        return capacity

    def calculate_segment_total_resistance(self):
        total_resistance = sum(pair.total_resistance for pair in self.cell_pairs)
        return total_resistance

    def calculate_average_ir_difference(self):
        if not self.cell_pairs:
            return 0
        total_ir_difference = sum(
            abs(pair.cell1.ir - pair.cell2.ir) for pair in self.cell_pairs if pair.cell1 and pair.cell2)
        return total_ir_difference / len(self.cell_pairs)

    def calculate_max_voltage_difference(self):
        return max(pair.voltage_difference for pair in self.cell_pairs) if self.cell_pairs else 0

class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[-1]

    def size(self):
        return len(self.items)

def read_csv_file(file_path):
    df = pd.read_csv(file_path, usecols=[1, 4, 5, 6], skiprows=1)
    cells = []
    for index, row in df.iterrows():
        cell = Cell(row[0], row[1], row[2], row[3])
        cells.append(cell)
    return cells

def remove_low_capacity_cells(cells, num_segments, num_pairs_per_segment):
    filtered_cells = [cell for cell in cells if cell.number not in [269, 270]]
    filtered_cells.sort(key=lambda x: x.capacity, reverse= True)
    k = num_segments * num_pairs_per_segment * 2
    high_cap_cells = filtered_cells[:k]
    low_cap_cells = filtered_cells[k:]

    special_cells = [cell for cell in cells if cell.number in [269, 270]]
    low_cap_cells.extend(special_cells)
    low_cap_cells.sort(key=lambda x:x.capacity, reverse=True)
    if (len(low_cap_cells)-1)%2 != 0:
        removed_cell = low_cap_cells.pop()
        print(f"Cell numner {removed_cell.number} är lämnad och inte parad.")
    return high_cap_cells, low_cap_cells

def pair_extra_cells(cells, starting_pair_number=1):
    paired_cells = []
    pair_number = starting_pair_number

    while len(cells) > 1:
        cell1 = cells.pop(0)
        best_pair_index = None
        best_diff = float('inf')
        for i, cell2 in enumerate(cells):
            diff = abs(cell1.ir - cell2.ir)
            if diff < best_diff:
                best_pair_index = i
                best_diff = diff
        if best_pair_index is not None:
            cell2 = cells.pop(best_pair_index)
            new_pair = CellPair(cell1, cell2)
            new_pair.pair_number = pair_number
            paired_cells.append(new_pair)
            pair_number += 1

    return paired_cells

def pair_cells_based_on_ir(cells):
    cell_pairs = []
    paired_cells = set()

    for i, cell1 in enumerate(cells):
        if cell1 in paired_cells:
            continue

        min_difference_ir = float('inf')
        best_pair = None
        for j, cell2 in enumerate(cells):
            if i != j and cell2 not in paired_cells:
                difference_ir = abs(cell1.ir - cell2.ir)
                difference_mV = abs(cell1.voltage-cell2.voltage)
                if difference_ir < min_difference_ir and difference_mV < 3:
                    min_difference_ir = difference_ir
                    best_pair = CellPair(cell1, cell2)

        if best_pair is not None:
            cell_pairs.append(best_pair)
            paired_cells.add(cell1)
            paired_cells.add(best_pair.cell2)

    for i, pair in enumerate(cell_pairs, start=1):
        pair.pair_number = i
    return cell_pairs

def sort_diversity_stack(diversity_cells):
    sorted_stack = sorted(diversity_cells, key=lambda x: (
        x.voltage_difference,
        x.ir_difference,
        x.capacity_difference
    ), reverse=True)
    return sorted_stack

def Segment_pairing_solution(cell_pairs, num_pairs_per_segment):
    pairs_final_sorted = []
    segments = []
    pairs_sorted_on_ir = sorted(cell_pairs, key=lambda x: x.total_resistance)
    pairs_sorted_on_diversity = sort_diversity_stack(cell_pairs)
    high_ir_pairs = Stack()
    diversity_pairs = Stack()

    for pair in pairs_sorted_on_ir:
        high_ir_pairs.push(pair)

    for pair in pairs_sorted_on_diversity:
        diversity_pairs.push(pair)

    while not (high_ir_pairs.isEmpty() and diversity_pairs.isEmpty()):
        if not diversity_pairs.isEmpty():
            add1 = diversity_pairs.pop()
            if not diversity_pairs.isEmpty():
                add2 = diversity_pairs.pop()
            else:
                add2 = None
        else:
            add1 = add2 = None

        if not high_ir_pairs.isEmpty():
            add3 = high_ir_pairs.pop()
        else:
            add3 = None

        if add1 and add1 not in pairs_final_sorted:
            pairs_final_sorted.append(add1)
        if add2 and add2 not in pairs_final_sorted:
            pairs_final_sorted.append(add2)
        if add3 and add3 not in pairs_final_sorted:
            pairs_final_sorted.append(add3)

    for i in range(0, len(pairs_final_sorted), num_pairs_per_segment):
        segment_pairs = pairs_final_sorted[i:i + num_pairs_per_segment]
        segment = Segment(segment_pairs)
        segments.append(segment)

    segments.sort(key=lambda segment: segment.segment_total_resistance, reverse=True)

    return segments

def print_segments(segments):
    pair_header = "{:<10} {:<10} {:<15} {:<15} {:<15} {:<10} {:<15} {:<15} {:<15} {:<25} {:<15} {:<15}".format(
        "Segment", "Pair Nr", "Cell Pair", "Cell 1 V", "Cell 1 IR",
        "Cell 1 mAh", "Cell 2 V", "Cell 2 IR",
        "Cell 2 mAh", "Diff Voltage", "Combined IR", "Similarity Score"
    )
    print(pair_header)
    print("-" * len(pair_header))

    battery_capacity = float('inf')
    for idx, segment in enumerate(segments):
        for pair in segment.cell_pairs:
            line = "{:<10} {:<10} {:<15} {:<15} {:<15} {:<10} {:<15} {:<15} {:<15} {:<25} {:<15} {:<15}".format(
                f"{idx + 1}",
                f"{pair.pair_number}",
                f"{pair.cell1.number}-{pair.cell2.number}",
                f"{pair.cell1.voltage}mV", f"{pair.cell1.ir}Ω",
                f"{pair.cell1.capacity}mAh", f"{pair.cell2.voltage}mV",
                f"{pair.cell2.ir}Ω", f"{pair.cell2.capacity}mAh",
                f"{pair.voltage_difference}mV", f"{pair.total_resistance:.2f}Ω",
                f"{pair.similarity_score}"
            )
            print(line)

        segment_footer = "\nSegment Total Capacity: {} mAh\nSegment Total Resistance: {:.2f} mOhm\nAverage IR Difference: {:.2f} mOhm".format(
            segment.segment_total_capacity, segment.segment_total_resistance, segment.average_ir_difference
        )
        print(segment_footer)
        print("-" * len(pair_header))

        battery_capacity = min(battery_capacity, segment.segment_total_capacity)

    print(f'Battery capacity: {battery_capacity}mAh')
    print("-" * len(pair_header))

def write_to_file(segments, spairssegment, filename="output.txt"):
    with open(filename, "w", encoding='utf-8') as file:
        def write_segment_data(segment):
            file.write("Segments:\n")
            header = "{:<10} {:<15} {:<15} {:<10} {:<15} {:<15} {:<15} {:<15} {:<25} {:<15} {:<15}\n".format(
                "Segment", "Pair Number", "Cell Pair", "Cell 1 Voltage", "Cell 1 IR",
                "Cell 1 Capacity", "Cell 2 Voltage", "Cell 2 IR",
                "Cell 2 Capacity", "Diff Voltage", "Combined IR", "Similarity Score"
            )
            file.write(header)
            file.write("-" * len(header) + "\n")

            for idx, seg in enumerate(segment):
                for pair in seg.cell_pairs:
                    line = "{:<10} {:<15} {:<15} {:<10} {:<15} {:<15} {:<15} {:<15} {:<15} {:<25} {:<15} {:<15}\n".format(
                        f"{idx + 1}",
                        f"{pair.pair_number}",
                        f"{pair.cell1.number}-{pair.cell2.number}",
                        f"{pair.cell1.voltage}mV", f"{pair.cell1.ir}Ω",
                        f"{pair.cell1.capacity}mAh", f"{pair.cell2.voltage}mV",
                        f"{pair.cell2.ir}Ω", f"{pair.cell2.capacity}mAh",
                        f"{pair.voltage_difference}mV", f"{pair.total_resistance:.2f}Ω",
                        f"{pair.similarity_score}"
                    )
                    file.write(line)

                segment_footer = "\nSegment Total Capacity: {} mAh\nSegment Total Resistance: {:.2f} mOhm\nAverage IR Difference: {:.2f} mOhm\n".format(
                    seg.segment_total_capacity, seg.segment_total_resistance, seg.average_ir_difference
                )
                file.write(segment_footer)
                file.write("-" * len(header) + "\n")

        write_segment_data(segments)
        if spairssegment:
            file.write("Spare Pairs Segment:\n")
            write_segment_data(spairssegment)

def write_segments_to_excel(segments, spairssegment, filename="output_segments.xlsx"):
    def prepare_segment_data_for_excel(segments):
        data = []
        for idx, segment in enumerate(segments):
            for pair in segment.cell_pairs:
                row = [
                    f"Segment {idx + 1}",
                    f"{pair.pair_number}",
                    f"{pair.cell1.number}-{pair.cell2.number}",
                    pair.cell1.voltage, pair.cell1.ir,
                    pair.cell1.capacity, pair.cell2.voltage,
                    pair.cell2.ir, pair.cell2.capacity,
                    pair.voltage_difference, pair.total_resistance,
                    pair.similarity_score
                ]
                data.append(row)
        return data

    all_data = prepare_segment_data_for_excel(segments) + prepare_segment_data_for_excel(spairssegment)
    df = pd.DataFrame(all_data, columns=[
        "Segment", "Pair Number", "Cell Pair", "Cell 1 Voltage", "Cell 1 IR",
        "Cell 1 Capacity", "Cell 2 Voltage", "Cell 2 IR", "Cell 2 Capacity",
        "Diff Voltage", "Combined IR", "Similarity Score"
    ])

    df.to_excel(filename, index=False)

def main():
    file_path = "Cell-information.csv" #input("Enter the path to the CSV file: ").strip('"')
    cells = read_csv_file(file_path)
    num_segments = 6 #int(input("Enter the number of segments: "))
    num_pairs_per_segment = 21 #int(input("Enter the number of cell pairs per segment: "))
    cells, extra_cells = remove_low_capacity_cells(cells, num_segments, num_pairs_per_segment)
    ###
    high_ir_pairs = pair_cells_based_on_ir(cells)
    paired_extra_cells = pair_extra_cells(extra_cells)
    segments = Segment_pairing_solution(high_ir_pairs,num_pairs_per_segment)
    spairssegment = Segment_pairing_solution(paired_extra_cells, num_pairs_per_segment)
    print_segments(segments)
    print_segments(spairssegment)
    write_to_file(segments, spairssegment)
    print("Data has been saved in output.txt.")
    write_segments_to_excel(segments, spairssegment, "output_segments.xlsx")
    print("Segments and spare pairs data have been saved to output_segments.xlsx.")
    ###

if __name__ == "__main__":
    main()


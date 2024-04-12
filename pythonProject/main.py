import pandas as pd
import random
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
        self.total_capacity = self.total_capacity()
        self.total_resistance = self.total_resistance()
        self.total_voltage = self.total_voltage()
        self.diff_voltage = self.diff_voltage()

    def calculate_similarity(self):
        voltage_diff = abs(self.cell1.voltage - self.cell2.voltage)
        resistance_diff = abs(self.cell1.ir - self.cell2.ir)
        capacity_diff = abs(self.cell1.capacity - self.cell2.capacity)
        return voltage_diff + resistance_diff + capacity_diff

    def total_capacity(self):
        if self.cell1 and self.cell2 is not None:
            total = self.cell1.capacity + self.cell2.capacity
        return total

    def total_resistance(self):
        if self.cell1 and self.cell2 is not None:
            total = 1 / ((1 / self.cell1.ir) + (1 / self.cell2.ir))
        return total
    def total_voltage(self):
        if self.cell1.voltage < self.cell2.voltage:
            total_voltage= self.cell1.voltage
        else:
            total_voltage= self.cell2.voltage
        return total_voltage

    def diff_voltage(self):
        voltage_diff = abs(self.cell1.voltage - self.cell2.voltage)
        return voltage_diff

class Segment:
    def __init__(self, cell_pairs):
        self.cell_pairs = cell_pairs
        self.segment_total_resistance = self.calculate_segment_total_resistance()
        self.segment_total_capacity = self.calculate_segment_total_capacity()
        self.average_ir_difference = self.calculate_average_ir_difference()
        self.max_voltage_difference = self.max_voltage_difference()
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

    def max_voltage_difference(self):
        return max(pair.diff_voltage for pair in self.cell_pairs) if self.cell_pairs else 0

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
    # Assuming starting_pair_number is correctly calculated before this function is called
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
            pair_number += 1  # Increment the pair_number for the next pair

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
                if difference_ir < min_difference_ir and difference_mV < 4:
                    min_difference_ir = difference_ir
                    best_pair = CellPair(cell1, cell2)

        if best_pair is not None:
            cell_pairs.append(best_pair)
            paired_cells.add(cell1)
            paired_cells.add(best_pair.cell2)

    for i, pair in enumerate(cell_pairs, start=1):
        pair.pair_number = i
    return cell_pairs
def create_segments_based_on_resistance(cell_pairs, num_pairs_per_segment):
    segments = []
    for i in range(0, len(cell_pairs), num_pairs_per_segment):
        segment_pairs = cell_pairs[i:i + num_pairs_per_segment]
        segment_pairs.sort(key=lambda x: x.total_resistance)
        segment = Segment(segment_pairs)
        segments.append(segment)
    return segments

def create_segments_based_on_ir(cell_pairs, num_pairs_per_segment):
    best_segments = None
    best_total_resistance = float('inf')
    V_diff = float("inf")

    for _ in range(10000):
        shuffled_pairs = random.sample(cell_pairs, len(cell_pairs))
        segments = []

        for i in range(0, len(shuffled_pairs), num_pairs_per_segment):
            segment_pairs = shuffled_pairs[i:i + num_pairs_per_segment]
            segment = Segment(segment_pairs)
            segments.append(segment)

        total_resistance = sum(segment.segment_total_resistance for segment in segments)
        max_voltage_diff = max(segment.max_voltage_difference for segment in segments)

        if total_resistance < best_total_resistance and max_voltage_diff < V_diff:
            best_total_resistance = total_resistance
            best_segments = segments
    return best_segments


def create_segments_even_every_forth_is_highest_ir(cell_pairs, num_pairs_per_segment):
    cell_pairs_sorted_by_similarity = sorted(cell_pairs, key=lambda x: x.similarity_score)
    cell_pairs_sorted_by_ir = sorted(cell_pairs, key=lambda x: max(x.cell1.ir, x.cell2.ir), reverse=True)
    num_high_ir_pairs_needed = (len(cell_pairs_sorted_by_similarity) // 4) + (
        0 if len(cell_pairs_sorted_by_similarity) % 4 == 0 else 1)
    high_ir_pairs = cell_pairs_sorted_by_ir[:num_high_ir_pairs_needed]

    reordered_pairs = cell_pairs_sorted_by_similarity[:]


    insert_positions = range(0, len(reordered_pairs), 4)
    for position, high_ir_pair in zip(insert_positions, high_ir_pairs):
        if position < len(reordered_pairs):
            reordered_pairs[position] = high_ir_pair
        else:
            break

    remaining_pairs = [pair for pair in cell_pairs_sorted_by_similarity if pair not in high_ir_pairs]
    for i, pair in enumerate(remaining_pairs):
        if not reordered_pairs[i]:
            reordered_pairs[i] = pair

    segments = []
    for i in range(0, len(reordered_pairs), num_pairs_per_segment):
        segment = Segment(reordered_pairs[i:i + num_pairs_per_segment])
        segments.append(segment)

    return segments
def create_segments_sorted_by_ir(cell_pairs, num_pairs_per_segment):
    sorted_pairs = sorted(cell_pairs, key=lambda x: x.total_resistance, reverse=True)
    segments = []
    for i in range(0, len(sorted_pairs), num_pairs_per_segment):
        segment_pairs = sorted_pairs[i:i + num_pairs_per_segment]
        segment = Segment(segment_pairs)
        segments.append(segment)

    return segments

def calculate_mean_attributes(cell_pairs):
    total_resistance_mean = sum(pair.total_resistance for pair in cell_pairs) / len(cell_pairs)
    total_voltage_mean = sum(pair.total_voltage for pair in cell_pairs) / len(cell_pairs)
    total_capacity_mean = sum(pair.total_capacity for pair in cell_pairs) / len(cell_pairs)
    return total_resistance_mean, total_voltage_mean, total_capacity_mean

def score_cell_pairs(cell_pairs, means):
    scores = []
    for pair in cell_pairs:
        score = abs(pair.total_resistance - means[0]) + abs(pair.total_voltage - means[1]) + abs(
            pair.total_capacity - means[2])
        scores.append((score, pair))
    return scores
def test(cell_pairs, num_pairs_per_segment):
    pairs_sorted_on_ir = sorted(cell_pairs, key=lambda x: x.total_resistance, reverse=True)
    pairs_final_sorted = []
    segments = []
    for i in range(0, len(cell_pairs), num_pairs_per_segment):
        # Select a subset of cell pairs for this segment.
        segment_pairs = cell_pairs[i:i + num_pairs_per_segment]

        # Calculate mean attributes and score cell pairs based on diversity.
        means = calculate_mean_attributes(segment_pairs)
        scored_pairs = score_cell_pairs(segment_pairs, means)
        scored_pairs.sort(key=lambda x: x[0], reverse=True)
    while True:
        if scored_pairs:
            return False
        add1 = scored_pairs.pop()
        add2 = scored_pairs.pop()
        add3= pairs_sorted_on_ir.pop()
        if add1 not in pairs_final_sorted:
            pairs_final_sorted.append(add1)
        if add2 not in pairs_final_sorted:
            pairs_final_sorted.append(add2)
        if add3 not in pairs_final_sorted:
            pairs_final_sorted.append(add3)

    for i in range(0, len(pairs_final_sorted), num_pairs_per_segment):
        segment_pairs = pairs_final_sorted[i:i + num_pairs_per_segment]
        segment = Segment(segment_pairs)
        segments.append(segment)
    return segments

def create_segments_with_diversity_and_high_ir(cell_pairs, num_pairs_per_segment):
    # Sort cell pairs by their internal resistance, from highest to lowest.
    pairs_sorted_on_ir = sorted(cell_pairs, key=lambda x: x.total_resistance, reverse=True)
    used_high_ir_pairs = set()  # Track used high IR pairs

    segments = []
    for i in range(0, len(cell_pairs), num_pairs_per_segment):
        # Select a subset of cell pairs for this segment.
        segment_pairs = cell_pairs[i:i + num_pairs_per_segment]

        # Calculate mean attributes and score cell pairs based on diversity.
        means = calculate_mean_attributes(segment_pairs)
        scored_pairs = score_cell_pairs(segment_pairs, means)
        scored_pairs.sort(key=lambda x: x[0], reverse=True)

        # Select cell pairs for the segment based on their diversity scores.
        selected_pairs = [pair for _, pair in scored_pairs[:num_pairs_per_segment]]

        # Determine the number of high IR pairs to insert into the segment.
        num_insertions = min(len(selected_pairs) // 3, len(pairs_sorted_on_ir))
        for j in range(num_insertions):
            insert_position = (j + 1) * 4 - 1

            # Find the next high IR pair not yet used.
            while pairs_sorted_on_ir and pairs_sorted_on_ir[0] in used_high_ir_pairs:
                pairs_sorted_on_ir.pop(0)  # Remove already used pairs

            if insert_position < len(selected_pairs) and pairs_sorted_on_ir:
                high_ir_pair = pairs_sorted_on_ir.pop(0)  # Safely remove the next high IR pair

                # Insert the high IR pair at the calculated position.
                selected_pairs.insert(insert_position, high_ir_pair)
                used_high_ir_pairs.add(high_ir_pair)  # Mark this pair as used

        # Create a new Segment with the selected pairs, including the inserted high IR pairs.
        segment = Segment(selected_pairs)
        segments.append(segment)

    # Optionally, sort the segments by total resistance in descending order.
    segments.sort(key=lambda segment: segment.segment_total_resistance, reverse=True)

    return segments

def print_segments(segments):
    pair_header = "{:<10} {:<10} {:<15} {:<15} {:<15} {:<10} {:<15} {:<15} {:<15} {:<25} {:<15} {:<15}".format(
        "Segment", "Pair Number", "Cell Pair", "Cell 1 Voltage", "Cell 1 IR",
        "Cell 1 Capacity", "Cell 2 Voltage", "Cell 2 IR",
        "Cell 2 Capacity", "Diff Voltage", "Combined IR", "Similarity Score"
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
                f"{pair.diff_voltage}mV", f"{pair.total_resistance:.2f}Ω",
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
                    line = "{:<10} {:<15} {:<15} {:<10} {:<15} {:<15} {:<15} {:<15} {:<25} {:<15} {:<15}\n".format(
                        f"{idx + 1}",
                        f"{pair.pair_number}",
                        f"{pair.cell1.number}-{pair.cell2.number}",
                        f"{pair.cell1.voltage}mV", f"{pair.cell1.ir}Ω",
                        f"{pair.cell1.capacity}mAh", f"{pair.cell2.voltage}mV",
                        f"{pair.cell2.ir}Ω", f"{pair.cell2.capacity}mAh",
                        f"{pair.diff_voltage}mV", f"{pair.total_resistance:.2f}Ω",
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
    import pandas as pd  # Ensure pandas is imported

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
                    pair.diff_voltage, pair.total_resistance,
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
    test(high_ir_pairs,num_pairs_per_segment)
    segments = test(high_ir_pairs, num_pairs_per_segment)
    spairssegment = test(paired_extra_cells, num_pairs_per_segment)
    print_segments(segments)
    print_segments(spairssegment)
    write_to_file(segments, spairssegment)
    print("Data has been saved in output.txt.")
    write_segments_to_excel(segments, spairssegment, "output_segments.xlsx")
    print("Segments and spare pairs data have been saved to output_segments.xlsx.")
    ###

if __name__ == "__main__":
    main()


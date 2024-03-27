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
        self.cell1 = cell1
        self.cell2 = cell2
        self.similarity_score = self.calculate_similarity()
        self.total_capacity = self.total_capacity()
        self.total_resistance = self.total_resistance()

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

class Segment:
    def __init__(self, cell_pairs):
        self.cell_pairs = cell_pairs
        self.segment_total_resistance = self.calculate_segment_total_resistance()
        self.segment_total_capacity = self.calculate_segment_total_capacity()
        self.average_ir_difference = self.calculate_average_ir_difference()

    def calculate_segment_total_capacity(self):
        capacity = 100000000000
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

def read_csv_file(file_path):
    df = pd.read_csv(file_path, usecols=[1, 4, 5, 6], skiprows=1)
    cells = []
    for index, row in df.iterrows():
        cell = Cell(row[0], row[1], row[2], row[3])
        cells.append(cell)
    return cells


def remove_low_capacity_cells(cells, num_segments, num_pairs_per_segment):
    filtered_cells = [cell for cell in cells if cell.number not in [269, 270]]
    filtered_cells.sort(key=lambda x: x.capacity)
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


def pair_extra_cells(cells):
    """
    Pair extra cells based on their internal resistance (IR) to minimize the difference in IR.

    :param cells: List of Cell objects to be paired.
    :return: List of CellPair objects created from the input cells.
    """
    paired_cells = []
    while len(cells) > 1:
        cell1 = cells.pop(0)  # Remove and get the first cell

        # Find the best pair for cell1 based on the smallest IR difference
        best_pair = None
        best_diff = float('inf')
        for i, cell2 in enumerate(cells):
            diff = abs(cell1.ir - cell2.ir)
            if diff < best_diff:
                best_pair = i
                best_diff = diff

        # If a pair was found, create a CellPair object and add to the list
        if best_pair is not None:
            cell2 = cells.pop(best_pair)
            paired_cells.append(CellPair(cell1, cell2))

    return paired_cells


def pair_cells_melasta(cells):
    cell_pairs = []
    for i in range(0, len(cells), 2):
        if i + 1 < len(cells):
            pair = CellPair(cells[i], cells[i + 1])
            cell_pairs.append(pair)
    return cell_pairs

def pair_cells_by_similarity(cells):
    cell_pairs = pair_cells_melasta(cells)
    cell_pairs.sort(key=lambda x: x.similarity_score)
    return cell_pairs

def pair_cells_on_ir(cells):
    cell_pairs = []
    paired_cells = set()  # Keep track of paired cells
    for i, cell1 in enumerate(cells):
        if cell1 in paired_cells:  # Skip already paired cells
            continue
        dif = float("inf")
        cell_pair = None
        for j, cell2 in enumerate(cells):
            if i != j and cell2 not in paired_cells:  # Check if cell2 is not already paired
                d = abs(cell1.ir - cell2.ir)
                if d < dif:
                    dif = d
                    cell_pair = CellPair(cell1, cell2)
        if cell_pair is not None:
            cell_pairs.append(cell_pair)
            paired_cells.add(cell1)
            paired_cells.add(cell_pair.cell2)
    return cell_pairs

def match_cell_pairs_based_on(cells, num_pairs):
    cell_pairs = pair_cells_on_ir(cells)
    cell_pairs.sort(key=lambda x: x.total_resistance)
    high_resistance_cells = cell_pairs[:num_pairs]
    return high_resistance_cells

def pair_cells_based_on_ir(cells):
    cell_pairs = []
    paired_cells = set()  # Keep track of paired cells

    for i, cell1 in enumerate(cells):
        if cell1 in paired_cells:  # Skip already paired cells
            continue

        min_difference = float('inf')
        best_pair = None

        for j, cell2 in enumerate(cells):
            if i != j and cell2 not in paired_cells:  # Check if cell2 is not already paired
                difference = abs(cell1.ir - cell2.ir)
                if difference < min_difference:
                    min_difference = difference
                    best_pair = CellPair(cell1, cell2)

        if best_pair is not None:
            cell_pairs.append(best_pair)
            paired_cells.add(cell1)
            paired_cells.add(best_pair.cell2)

    return cell_pairs

def create_segments(cell_pairs, num_pairs_per_segment):
    segments = []
    for i in range(0, len(cell_pairs), num_pairs_per_segment):
        segment = Segment(cell_pairs[i:i + num_pairs_per_segment])
        segments.append(segment)
    return segments

def create_segments_based_on_resistance(cell_pairs, num_pairs_per_segment):
    segments = []
    for i in range(0, len(cell_pairs), num_pairs_per_segment):
        segment_pairs = cell_pairs[i:i + num_pairs_per_segment]

        # Sort segment pairs based on IR
        segment_pairs.sort(key=lambda x: x.total_resistance)

        # Create segment
        segment = Segment(segment_pairs)
        segments.append(segment)

    return segments

def create_segments_based_on_ir(cell_pairs, num_pairs_per_segment):
    best_segments = None
    best_total_resistance = float('inf')

    for _ in range(10000):  # Run multiple iterations to find the best combination
        shuffled_pairs = random.sample(cell_pairs, len(cell_pairs))  # Shuffle the cell pairs
        segments = []

        for i in range(0, len(shuffled_pairs), num_pairs_per_segment):
            segment_pairs = shuffled_pairs[i:i + num_pairs_per_segment]
            segment = Segment(segment_pairs)
            segments.append(segment)

        total_resistance = sum(segment.segment_total_resistance for segment in segments)

        if total_resistance < best_total_resistance:
            best_total_resistance = total_resistance
            best_segments = segments

    return best_segments

def print_segments(segments):
    print("Segments:")
    print("{:<10} {:<30} {:<61} {:<30}".format("Segment", "Cell Pair", "Cell 1 Properties", "Cell 2 Properties"))
    for idx, segment in enumerate(segments):
        print(f"Segment {idx + 1} (Average IR Difference: {segment.average_ir_difference:.2f}):")
        for pair in segment.cell_pairs:
            print("{:<10} {:<30} {:<30} {:<30}".format(idx + 1,
                                                        f"{pair.cell1.number}-{pair.cell2.number}",
                                                        f"Voltage (mV): {pair.cell1.voltage}, IR (mOhm): {pair.cell1.ir}, Capacity (mAh): {pair.cell1.capacity}",
                                                        f"Voltage (mV): {pair.cell2.voltage}, IR (mOhm): {pair.cell2.ir}, Capacity (mAh): {pair.cell2.capacity}"))
        print("{:<10} {:<30} {:<30} {:<30}".format("", "Total Resistance:",
                                                    f"{segment.segment_total_resistance:.2f} mOhm", ""))
        print("{:<10} {:<30} {:<30} {:<30}".format("", "Total Capacity:", f"{segment.segment_total_capacity} mAh", ""))
        print("-" * 100)  # Streckad linje mellan segmenten
    print()
def write_to_file(segments, spairssegment, filename="output.txt"):
    with open(filename, "w") as file:
        def write_segment_data(segment):
            file.write("Segments:\n")
            file.write("{:<10} {:<30} {:<61} {:<30}\n".format("Segment", "Cell Pair", "Cell 1 Properties", "Cell 2 Properties"))
            for idx, segment in enumerate(segment):
                file.write(f"Segment {idx + 1} (Average IR Difference: {segment.average_ir_difference:.2f}):\n")
                for pair in segment.cell_pairs:
                    file.write("{:<10} {:<30} {:<30} {:<30}\n".format(idx + 1,
                                                                      f"{pair.cell1.number}-{pair.cell2.number}",
                                                                      f"Voltage (mV): {pair.cell1.voltage}, IR (mOhm): {pair.cell1.ir}, Capacity (mAh): {pair.cell1.capacity}",
                                                                      f"Voltage (mV): {pair.cell2.voltage}, IR (mOhm): {pair.cell2.ir}, Capacity (mAh): {pair.cell2.capacity}"))
                file.write("{:<10} {:<30} {:<30} {:<30}\n".format("", "Total Resistance:",
                                                                  f"{segment.segment_total_resistance:.2f} mOhm", ""))
                file.write("{:<10} {:<30} {:<30} {:<30}\n".format("", "Total Capacity:", f"{segment.segment_total_capacity} mAh", ""))
                file.write("-" * 100 + "\n")  # Streckad linje mellan segmenten
            file.write("\n")

        write_segment_data(segments)
        write_segment_data(spairssegment)


def write_segments_to_excel(segments, spairssegment, filename="output_segments.xlsx"):
    # Helper function to prepare data for Excel
    def prepare_segment_data_for_excel(segments):
        data = []
        for idx, segment in enumerate(segments):
            for pair in segment.cell_pairs:
                row = [
                    f"Segment {idx + 1}",
                    f"{pair.cell1.number}-{pair.cell2.number}",
                    f"{pair.cell1.voltage}",
                    f"{pair.cell1.ir}",
                    f"{pair.cell1.capacity}",
                    f"{pair.cell2.voltage}",
                    f"{pair.cell2.ir}",
                    f"{pair.cell2.capacity}",
                    segment.average_ir_difference,
                    f"{segment.segment_total_resistance:.2f}",
                    f"{segment.segment_total_capacity}"
                ]
                data.append(row)
        return data

    # Combine data from segments and spare pairs
    all_data = prepare_segment_data_for_excel(segments) + prepare_segment_data_for_excel(spairssegment)
    df = pd.DataFrame(all_data, columns=["Segment", "Cell Pair", "Cell 1 Voltage", "Cell 1 IR", "Cell 1 Capacity",
                                         "Cell 2 Voltage", "Cell 2 IR", "Cell 2 Capacity", "Average IR Difference",
                                         "Total Resistance", "Total Capacity"])

    # Write DataFrame to an Excel file
    df.to_excel(filename, index=False)
def main():
    file_path = "Cell-information.csv" #input("Enter the path to the CSV file: ").strip('"')
    cells = read_csv_file(file_path)
    num_segments = 6 #int(input("Enter the number of segments: "))
    num_pairs_per_segment = 21 #int(input("Enter the number of cell pairs per segment: "))
    cells, extra_cells = remove_low_capacity_cells(cells, num_segments, num_pairs_per_segment)
    while True:
        print("Ange A om du vill sortera på Melastas cellpar och sortering på alla egenskaper lika")
        print("Ange B om du vill göra egen cell parning baserat lägsta resistans skillnad och att segment vis kommer resistansen längre fram")
        print("Ange C om du vill gör egen cellparning med högsta och lägsta kapasitans och att segment vis kommer resistansen längre fram")
        print("Ange D om vill göra cellparing så att parningen får minsta skillnad i ir och ger oss högsta kapacitansen")
        print("Ange Q för att avsluta")
        val = input("=").upper()
        if val == "A":
            high_capacity_cells = pair_cells_by_similarity(cells)
            segments = create_segments(high_capacity_cells,num_pairs_per_segment)
            paired_extra_cells = pair_extra_cells(extra_cells)
            spairssegment = create_segments(paired_extra_cells,num_pairs_per_segment)
            output_choice = input("Print to terminal (T) or save to a text file (F)? or E for excel or S for all").strip().upper()
            if output_choice == 'T':
                print_segments(segments)
                print_segments(spairssegment)
            elif output_choice == 'E':  # Assuming 'E' is for Excel output
                write_segments_to_excel(segments, spairssegment, "output_segments.xlsx")
                print("Segments and spare pairs data have been saved to output_segments.xlsx.")
            else:
                write_to_file(segments, spairssegment)
                print("Data has been saved in output.txt.")
        elif val == "B":
            high_ir_pairs = match_cell_pairs_based_on(cells, num_pairs_per_segment)
            segments = create_segments(high_ir_pairs, num_pairs_per_segment)
            paired_extra_cells = pair_extra_cells(extra_cells)
            spairssegment = create_segments(paired_extra_cells, num_pairs_per_segment)
            output_choice = input("Print to terminal (T) or save to a text file (F)? or E for excel or S for all").strip().upper()
            if output_choice == 'T':
                print_segments(segments)
                print_segments(spairssegment)
            elif output_choice == 'E':  # Assuming 'E' is for Excel output
                write_segments_to_excel(segments, spairssegment, "output_segments.xlsx")
                print("Segments and spare pairs data have been saved to output_segments.xlsx.")
            else:
                write_to_file(segments, spairssegment)
                print("Data has been saved in output.txt.")
        elif val == "C":
            high_ir_pairs = pair_cells_based_on_ir(cells)
            segments = create_segments_based_on_ir(high_ir_pairs, num_pairs_per_segment)
            paired_extra_cells = pair_extra_cells(extra_cells)
            spairssegment = create_segments_based_on_ir(paired_extra_cells, num_pairs_per_segment)
            output_choice = input("Print to terminal (T) or save to a text file (F)? or E for excel or S for all").strip().upper()
            if output_choice == 'T':
                print_segments(segments)
                print_segments(spairssegment)
            elif output_choice == 'E':  # Assuming 'E' is for Excel output
                write_segments_to_excel(segments, spairssegment, "output_segments.xlsx")
                print("Segments and spare pairs data have been saved to output_segments.xlsx.")
            else:
                write_to_file(segments, spairssegment)
                print("Data has been saved in output.txt.")
        elif val == "D":
            high_ir_pairs = pair_cells_based_on_ir(cells)
            segments = create_segments_based_on_resistance(high_ir_pairs, num_pairs_per_segment)
            paired_extra_cells = pair_extra_cells(extra_cells)
            spairssegment = create_segments_based_on_resistance(paired_extra_cells, num_pairs_per_segment)
            output_choice = input("Print to terminal (T) or save to a text file (F)? or E for excel or S for all").strip().upper()
            if output_choice == 'T':
                print_segments(segments)
                print_segments(spairssegment)
            elif output_choice == 'E':  # Assuming 'E' is for Excel output
                write_segments_to_excel(segments, spairssegment, "output_segments.xlsx")
                print("Segments and spare pairs data have been saved to output_segments.xlsx.")
            elif output_choice == "S":
                print_segments(segments)
                print_segments(spairssegment)
                write_to_file(segments, spairssegment)
                write_segments_to_excel(segments, spairssegment, "output_segments.xlsx")
            elif output_choice=="F":
                write_to_file(segments, spairssegment)
                print("Data has been saved in output.txt.")
            elif output_choice=="Q":
                break
            else:
                print("du angav felaktigt alternativ")
        elif val == "Q":
            break

if __name__ == "__main__":
    main()


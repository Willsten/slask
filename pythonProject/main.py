import pandas as pd
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
        total = self.cell1.capacity + self.cell2.capacity
        return total

    def total_resistance(self):
        total = 1 / ((1 / self.cell1.ir) + (1 / self.cell2.ir))
        return total


class Segment:
    def __init__(self, cell_pairs):
        self.cell_pairs = cell_pairs
        self.segment_total_resistance = self.calculate_segment_total_resistance()
        self.segment_total_capacity = self.calculate_segment_total_capacity()

    def calculate_segment_total_capacity(self):
        capacity = 0
        for pair in self.cell_pairs:
            if pair.total_capacity > capacity:
                capacity = pair.total_capacity
            else:
                continue
        return capacity

    def calculate_segment_total_resistance(self):
        total_resistance = sum(pair.total_resistance for pair in self.cell_pairs)
        return total_resistance

def read_csv_file(file_path):
    df = pd.read_csv(file_path, usecols=[1, 4, 5, 6], skiprows=1)
    cells = []
    for index, row in df.iterrows():
        cell = Cell(row[0], row[1], row[2], row[3])
        cells.append(cell)
    return cells

def pair_cells_melasta(cells):
    cell_pairs = []
    for i in range(0, len(cells), 2):
        if i + 1 < len(cells):
            pair = CellPair(cells[i], cells[i + 1])
            cell_pairs.append(pair)
    return cell_pairs
def pair_cells_by_similarity(cells, num_pairs):
    cell_pairs = pair_cells_melasta(cells)
    cell_pairs.sort(key=lambda x: x.total_capacity)
    high_capacity_cells = cell_pairs[:num_pairs]
    extra_cells = cell_pairs[num_pairs:]
    high_capacity_cells.sort(key=lambda x: x.similarity_score)
    return high_capacity_cells, extra_cells

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
    if not cell_pairs:
        return []  # Return empty list if no cell pairs are generated
    cell_pairs.sort(key=lambda x: x.total_resistance)
    high_resistance_cells = cell_pairs[:num_pairs]
    extra_cells = cell_pairs[num_pairs:]  # Include remaining pairs in the extra cells list
    return high_resistance_cells, extra_cells


def create_segments(cell_pairs, num_segments, num_pairs_per_segment):
    segments = []
    for i in range(0, len(cell_pairs), num_pairs_per_segment):
        segment = Segment(cell_pairs[i:i + num_pairs_per_segment])
        segments.append(segment)
    return segments

def print_segments(segments):
    print("Segments:")
    print("{:<10} {:<30} {:<61} {:<30}".format("Segment", "Cell Pair", "Cell 1 Properties", "Cell 2 Properties"))
    for idx, segment in enumerate(segments):
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

def write_to_file(segments, remaining_pairs):
    with open("output.txt", "w") as f:
        f.write("Segments:\n")
        f.write("{:<10} {:<30} {:<61} {:<30}\n".format("Segment", "Cell Pair", "Cell 1 Properties",
                                                       "Cell 2 Properties"))
        for idx, segment in enumerate(segments):
            for pair in segment.cell_pairs:
                f.write("{:<10} {:<30} {:<30} {:<30}\n".format(idx + 1,
                                                               f"{pair.cell1.number}-{pair.cell2.number}",
                                                               f"Voltage (mV): {pair.cell1.voltage}, IR (mOhm): {pair.cell1.ir}, Capacity (mAh): {pair.cell1.capacity}",
                                                               f"Voltage (mV): {pair.cell2.voltage}, IR (mOhm): {pair.cell2.ir}, Capacity (mAh): {pair.cell2.capacity}"))
            f.write("{:<10} {:<30} {:<30} {:<30}\n".format("", "Total Resistance:",
                                                           f"{segment.segment_total_resistance:.2f} mOhm", ""))
            f.write("{:<10} {:<30} {:<30} {:<30}\n".format("", "Total Capacity:", f"{segment.segment_total_capacity} mAh", ""))
            f.write("-" * 100 + "\n")  # Streckad linje mellan segmenten
        f.write("\nRemaining Pairs:\n")
        for pair in remaining_pairs:
            f.write(f"Cell Pair: {pair.cell1.number}-{pair.cell2.number}\n")

def main():
    file_path = input("Enter the path to the CSV file: ").strip('"')
    cells = read_csv_file(file_path)
    num_segments = int(input("Enter the number of segments: "))
    num_pairs_per_segment = int(input("Enter the number of cell pairs per segment: "))
    while True:
        print("Ange A om du vill sortera på Melastas cellpar och sortering på alla egenskaper lika")
        print("Ange B om du vill göra egen cell parning baserat lägsta resistans skillnad och att segment vis kommer resistansen längre fram")
        print("Ange C om du vill gör egen cellparning med högsta och lägsta kapasitans och att segment vis kommer resistansen längre fram")
        print("Ange D om vill göra egenparning på ")
        print("Ange Q för att avsluta")
        val = input("=").upper()
        if val == "A":
            high_capacity_cells, extra_cells = pair_cells_by_similarity(cells, num_segments * num_pairs_per_segment)
            segments = create_segments(high_capacity_cells, num_segments, num_pairs_per_segment)
            remaining_pairs = [pair for pair in extra_cells]
            output_choice = input("Print to terminal (T) or save to a text file (F)? ").strip().upper()
            if output_choice == 'T':
                print_segments(segments)
            else:
                write_to_file(segments, remaining_pairs)
                print("Data has been saved in output.txt.")
        elif val == "B":
            high_ir_pairs, low_ir = match_cell_pairs_based_on(cells, num_pairs_per_segment)
            segments = create_segments(high_ir_pairs + low_ir, num_segments, num_pairs_per_segment)
            output_choice = input("Print to terminal (T) or save to a text file (F)? ").strip().upper()
            if output_choice == 'T':
                print_segments(segments)
            else:
                write_to_file(segments, low_ir)  # Pass low_ir for remaining pairs
                print("Data has been saved in output.txt.")
        elif val =="Q":
            break

if __name__ == "__main__":
    main()
#Emil vill att de ska skrivas ut i excel också
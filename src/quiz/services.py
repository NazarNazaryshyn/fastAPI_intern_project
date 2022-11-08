import csv


def write_to_csv(data: list, filename: str) -> None:
    with open(f"{filename}.csv", "w+") as file:
        write = csv.writer(file, delimiter="\n")
        write.writerow(data)
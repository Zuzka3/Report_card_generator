import multiprocessing
import os


def worker_process_report(name, grades, result_queue, disk_semaphore, print_lock):
    with disk_semaphore:
        with print_lock:
            print("Processing student: " + name)

        total = 0
        count = 0
        for g in grades:
            total = total + g
            count = count + 1

        average = total / count

        status = "Passed"

        if average >= 4.5:
            status = "Failed"

        elif average <= 1.5:
            has_bad_grade = False
            for g in grades:
                if g >= 3:
                    has_bad_grade = True
            if not has_bad_grade:
                status = "Distinction"

        filename = "report_" + name + ".txt"
        try:
            f = open(filename, "w")
            f.write("SCHOOL REPORT CARD\n")
            f.write("------------------\n")
            f.write("Name: " + name + "\n")
            f.write("Grades: " + str(grades) + "\n")
            f.write("Status: " + status + "\n")
            f.close()

        except Exception as e:
            print("Error writing file: " + str(e))

        result_queue.put([name, average, status])

def producer_load_and_run(filename):
    print("Producer: Loading file " + filename + "...")

    if not os.path.exists(filename):
        print("Error: File not found!")
        return None

    f = open(filename, "r")
    lines = f.readlines()
    f.close()

    student_list = []
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        parts = line.split(";")
        name = parts[0]
        grades = []
        for x in parts[1:]:
            grades.append(int(x))
        student_list.append([name, grades])

    print("Producer: Starting " + str(len(student_list)) + " processes...")

    queue = multiprocessing.Queue()
    semaphore = multiprocessing.Semaphore(2)
    lock = multiprocessing.Lock()

    processes = []

    for s in student_list:
        p = multiprocessing.Process(
            target=worker_process_report,
            args=(s[0], s[1], queue, semaphore, lock)
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print("Producer: All jobs finished.")
    return queue


def print_results(results_queue):
    print("\n=== FINAL STATISTICS ===")

    if results_queue is None:
        print("No results to show.")
        return

    count_distinction = 0
    count_failed = 0
    total_students = 0
    sum_averages = 0

    while not results_queue.empty():
        data = results_queue.get()
        name = data[0]
        avg = data[1]
        status = data[2]

        print(name + " -> Avg: " + str(round(avg, 2)) + " [" + status + "]")

        total_students = total_students + 1
        sum_averages = sum_averages + avg

        if status == "Distinction":
            count_distinction = count_distinction + 1
        elif status == "Failed":
            count_failed = count_failed + 1

    print("----------------------------")
    print("Total Students: " + str(total_students))
    print("Distinction: " + str(count_distinction))
    print("Failed: " + str(count_failed))

    if total_students > 0:
        class_avg = sum_averages / total_students
        print("Class Average: " + str(round(class_avg, 2)))


if __name__ == "__main__":
    print("=== SCHOOL GRADING SYSTEM STARTED ===")

    queue = producer_load_and_run("students.txt")

    print_results(queue)

    print("\n=== END OF PROGRAM ===")
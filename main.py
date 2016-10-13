import importlib.util
import os
import codecs
from subprocess import *
from pathlib import Path
from stu import *
from chardet.universaldetector import UniversalDetector
from datetime import datetime

# Homework config
# TODO: Use a json to save config
availableExt = ('.c',)
compiler = {
    '.c': 'gcc-6',
    '.cpp': 'g++-6'
}

# Select input folder
source_path = None
if importlib.util.find_spec('tkinter') is not None:
    import tkinter.filedialog
    import tkinter

    # print("Please select your input folder:")
    # while source_path is None:
    root = tkinter.Tk()
    root.update()
    source_path = tkinter.filedialog.askdirectory(title="Choose Homework source", mustexist=True)
    root.destroy()

else:
    while source_path is None:
        source_path = input('Please select your input folder: ')
        if not Path(source_path).exists():
            source_path = None

output_path = str(Path(source_path).joinpath('out'))
Path(output_path).mkdir(exist_ok=True)

print("Input: " + source_path)
print("Output: " + output_path)

# Get all homework file
files = []
for ext in availableExt:
    files.extend(Path(source_path).glob('*' + ext))

# For each file, Compile and Run
students = []
for file in files:
    file_path = str(file)
    # Add user data
    students.append(Student(file.stem))
    # Check encoding
    detector = UniversalDetector()
    with open(file_path, 'rb') as fin:
        line = fin.read()
        detector.reset()
        detector.feed(line)
        if detector.done:
            break
    detector.close()
    file_encoding = str(detector.result.get("encoding"))
    if file_encoding.lower() != "utf-8":
        BLOCKSIZE = 1048576  # or some other, desired size in bytes
        with codecs.open(file_path, "r", file_encoding.lower()) as sourceFile:
            with codecs.open(file_path + "utf8.c", "w", "utf-8") as targetFile:
                while True:
                    contents = sourceFile.read(BLOCKSIZE)
                    if not contents:
                        break
                    targetFile.write(contents)
        os.remove(file_path)
        os.rename(file_path + "utf8.c", file_path)
    # Compile
    pipeline = None
    binary = str(Path(output_path).joinpath(students[-1].nid + '.bin'))
    print("===============================")
    print(students[-1].name + " " + students[-1].nid + " (" + str(files.index(file)+1) + "/" + str(len(files)) + ")")
    print("===============================")
    try:
        pipeline = run(
            [compiler[file.suffix] + " \"" + file_path + "\" -o " + binary],
            stdout=PIPE, shell=True)
        if pipeline.stdout:
            print(pipeline.stdout.decode("utf-8"))
        if pipeline.returncode == 0:
            students[-1].status = Status.compile_success
            print("Compile successfully.")
        else:
            raise Exception('Compile Error!')
    except:
        students[-1].status = Status.compile_fail

    # Run
    writefile = False
    if students[-1].status == Status.compile_success:
        os.system(binary)
        students[-1].status = Status.run_success
        # Check Success
        if students[-1].status == Status.run_success:
            if writefile:
                # TODO: add auto current
                pass
            else:
                print()
                current = input('Does this homework current?[Y/n] ')
                if current == 'n' or current == 'N':
                    students[-1].status = Status.run_not_current
                else:
                    students[-1].status = Status.run_current

# Log all students
print()
print(">> Status: ")
fout = open(str(Path(output_path).joinpath(str(datetime.now())+".log")), 'w+')
for student in students:
    fout.write("{0}{1}: {2}\n".format(student.nid, student.name, student.status))
    print("{0}{1}: {2}".format(student.nid, student.name, student.status))
fout.close()
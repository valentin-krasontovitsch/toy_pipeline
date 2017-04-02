#   The starting data files would normally exist beforehand!
#       We create some empty files for this example
#


from ruffus import *
import os, random, sys


#   create fasta

starting_files = [
    ["a_R1.fastq", "a_R2.fastq"],
    ["b_R1.fastq", "b_R2.fastq"],
    ["c_R1.fastq", "c_R2.fastq"]
]

@originate(starting_files)
def create_test_files(output_file_name):
    sample_name = os.path.splitext(output_file_name)[0].split('_')[0]
    number_of_lines = random.randint(1,5)*2
    with open(output_file_name, "w") as output_file:
        for index in range(number_of_lines):
            output_file.write("{},{}\n".format(sample_name,
                index))
        print("    %s has %d lines" % (output_file_name, number_of_lines) )

#   split files

@subdivide(
        create_test_files,
        formatter(),
        "{path[0]}/{basename[0]}.*.fasta.part",
        "{path[0]}/{basename[0]}"
        )
def subdivide_files(input_file_name, output_file_names, output_file_name_stem):
    for file in output_file_names:
        os.unlink(file)
    number_of_output_files = 0
    for index, line in enumerate(open(input_file_name)):
        if index % 2 == 0:
            number_of_output_files += 1
            output_file_name = "%s.%d.fasta.part" % (output_file_name_stem, number_of_output_files)
            output_file = open(output_file_name, "w")
            print "    Subdivide %s -> %s" % (input_file_name, output_file_name)
        output_file.write(line)

#    merge files to a summary file

@merge(subdivide_files, "abc.vcf")
def call_variants(input_file_names, output_file_name):
    with open(output_file_name, "w") as output_file:
        for input_file_name in input_file_names:
            with open(input_file_name) as input_file:
                for _, line in enumerate(input_file):
                    output_file.write(line)

#    subdivide summary file by sample
@subdivide(call_variants, formatter(), "sample.*.vcf", "sample")
def seperate_by_sample(input_file_name, output_files, output_file_name_stem):
    read_samples = []
    with open(input_file_name) as input_file:
       for _, line in enumerate(input_file):
           sample_id = line.split(',')[0]
           if sample_id not in read_samples:
               read_samples.append(sample_id)
           with open(output_file_name_stem + "." + sample_id + ".vcf",
                     "a") as output_file:
               output_file.write(line)

#    filter sample summaries
@transform(seperate_by_sample, suffix(".vcf"), ".filtered.vcf")
def filter_even(input_file_name, output_file_name):
    with open(input_file_name) as input_file:
        with open(output_file_name, "w") as output_file:
            for _, line in enumerate(input_file):
                data = int(line.split(',')[1])
                if data % 2 == 0:
                    output_file.write(line)



#pipeline_printout(verbose=5)
pipeline_run(verbose=6)

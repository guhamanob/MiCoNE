#!/usr/bin/env nextflow

// Initialize variables
def sequences = params.sequences
def output_dir = file(params.output_dir)


// Parameters
def parameters = file(params.parameters)
def ncpus = params.ncpus // "-a -O $ncpus"

// Channels
Channel
    .fromPath(sequences)
    .ifEmpty { exit 1, "16S sequences not found" }
    .set { chnl_sequences }


// Processes

// Step1: Pick de novo otus
process pick_de_novo_otus {
    tag "${sequence_file.baseName}"
    publishDir "${output_dir}/denovo_picking"

    input:
    file sequence_file from chnl_sequences

    output:
    set file('otu_table.biom'), file('rep_seqs.fasta'), file('log*.txt') into output_chnl

    script:
    {{ pick_de_novo_otus }}
}

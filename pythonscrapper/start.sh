#!/bin/bash
#SBATCH -J SrapperJob        # job name
#SBATCH -o scrapperJob.o%j       # output and error file name (%j expands to jobID)
#SBATCH -n 32              # total number of mpi tasks requested
#SBATCH -p development     # queue (partition) -- normal, development, etc.
#SBATCH -t 20:30:00        # run time (hh:mm:ss) - 1.5 hours
#SBATCH --mail-user=ishwor.timilsina@mavs.uta.edu
#SBATCH --mail-type=begin  # email me when the job starts
#SBATCH --mail-type=end    # email me when the job finishes

ibrun python scrap.py              # run the MPI executable named a.out
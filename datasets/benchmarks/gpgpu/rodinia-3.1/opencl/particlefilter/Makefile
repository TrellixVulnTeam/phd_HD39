include ../../common/make.config
#OPENCL_DIR = /af21/den4gr/NVIDIA_GPU_Computing_SDK/

# C compiler
CC = g++
CC_FLAGS = -O2

ALL: OCL_particlefilter_naive OCL_particlefilter_double OCL_particlefilter_single

OCL_particlefilter_naive: ex_particle_OCL_naive_seq.o
	$(CC) $(CFLAGS) $(CC_FLAGS) ex_particle_OCL_naive_seq.o $(LDFLAGS) -o OCL_particlefilter_naive

OCL_particlefilter_double: ex_particle_OCL_double_seq.o
	$(CC) $(CFLAGS) $(CC_FLAGS) ex_particle_OCL_double_seq.o  $(LDFLAGS) -o OCL_particlefilter_double

OCL_particlefilter_single: ex_particle_OCL_single_seq.o
	$(CC) $(CFLAGS) $(CC_FLAGS) ex_particle_OCL_single_seq.o  $(LDFLAGS) -o OCL_particlefilter_single


%.o: %.[ch]
	$(CC) $(CC_FLAGS) $(CFLAGS) $< -c

ex_particle_OCL_naive_seq.o: ex_particle_OCL_naive_seq.cpp
	$(CC) $(CC_FLAGS) $(CFLAGS) ex_particle_OCL_naive_seq.cpp -c

ex_particle_OCL_double_seq.o: ex_particle_OCL_double_seq.cpp
	$(CC) $(CC_FLAGS) $(CFLAGS) ex_particle_OCL_double_seq.cpp -c

ex_particle_OCL_single_seq.o: ex_particle_OCL_single_seq.cpp
	$(CC) $(CC_FLAGS) $(CFLAGS) ex_particle_OCL_single_seq.cpp -c

clean:
	rm -f *.o *~ OCL_particlefilter_naive OCL_particlefilter_double OCL_particlefilter_single *.linkinfo

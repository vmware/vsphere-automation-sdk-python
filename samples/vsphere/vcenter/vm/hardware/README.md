This directory contains the samples for the vCenter VM hardware APIs.

You have two options to run samples inside this package:

1.  Run the whole test suite contains all vcenter samples using main.py in
    setup package. Please see README in setup package for detailed steps.

2.  Run individual sample on existing environment. You can either pass the
    environment parameters through command line arguments or specify them in
    setup.py in setup package. TODO: have property file in each test folder.

    For example, to run memory sample in vcenter.vm.hardware package:

    * Navigate to bin folder.

    * To run the sample with settings specified in setup.py
      in linux machine:

       $ ./run_sample.sh ../samples/vcenter/vm/hardware/memory.py

    * Or specify the credentials via command line input:

       $ ./run_sample.sh ../samples/vcenter/vm/hardware/memory.py \
            -s <server> -u <username> -p <password> -n <vm_name>
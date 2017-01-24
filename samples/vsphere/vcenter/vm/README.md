This directory contains samples for vCenter virtual machine APIs:

1. Virtual machine Create, Read and Delete operations:
    * Create a virtual machine with system provided defaults    - create/create_default_vm.py
    * Create a basic virtual machine                            - create/create_basic_vm.py
    * Create a exhaustive virtual machine                       - create/create_exhaustive_vm.py

2. Virtual machine power lifecycle (requires an existing virtual machine):
    * Manage virtual machine power state                        - power.py

3. Update virtual machine hardware settings (requires an existing virtual machine):
    * Configure virtual SATA adapters of a virtual machine      - hardware/adapter/sata.py
    * Configure virtual SCSI adapters of a virtual machine      - hardware/adapter/scsi.py
    * Configure the booting settings for virtual machine        - hardware/boot.py
    * Configure the boot devices used by a virtual machine      - hardware/boot_device.py
    * Configure CD-ROM devices for a virtual machine            - hardware/cdrom.py
    * Configure CPU settings for a virtual machine              - hardware/cpu.py
    * Configure disk settings for a virtual machine             - hardware/disk.py
    * Configure virtual ethernet adapters of a virtual machine  - hardware/ethernet.py
    * Configure Floppy settings for a virtual machine           - hardware/floppy.py
    * Configure Memory settings of a virtual machine            - hardware/memory.py
    * Configure Parallel ports for a virtual machine            - hardware/parallel.py
    * Configure Serial ports for a virtual machine              - hardware/serial.py

You have two options to run samples inside this package:

1.  Run the whole sample suite which contains all vcenter samples using main.py
    in samples.vsphere.vcenter.setup package.
    Please see the README in the setup package for detailed steps.

2.  Run an individual sample in an existing environment.
    You can either pass the testbed settings through command line
    arguments or specify them in setup.py in the setup package.

    For example, to run the create_default_vm sample in the samples.vsphere.vcenter.vm.create package:

    * $ cd /path/to/vsphere-automation-sdk-python-samples/bin

    * Run the sample with the testbed settings specified in setup.py in a Linux machine:

       $ ./run_sample.sh ../samples/vsphere/vcenter/vm/create/create_default_vm.py -v

    * Or specify the credentials using command line parameters:

       $ ./run_sample.sh ../samples/vsphere/vcenter/vm/create/create_default_vm.py -s &lt;server&gt; -u &lt;username&gt; -p &lt;password&gt; -v

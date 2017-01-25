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
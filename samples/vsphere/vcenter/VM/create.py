guest_os = testbed.config['VM_GUESTOS']

boot_disk = Disk.CreateSpec(type=Disk.HostBusAdapterType.SCSI,
                            scsi=ScsiAddressSpec(bus=0, unit=0),
                            new_vmdk=Disk.VmdkCreateSpec())
data_disk = Disk.CreateSpec(new_vmdk=Disk.VmdkCreateSpec())

nic = Ethernet.CreateSpec(
    start_connected=True,
    backing=Ethernet.BackingSpec(
        type=Ethernet.BackingType.STANDARD_PORTGROUP,
        network=standard_network))

boot_device_order = [
    BootDevice.EntryCreateSpec(BootDevice.Type.ETHERNET),
    BootDevice.EntryCreateSpec(BootDevice.Type.DISK)]

vm_create_spec = VM.CreateSpec(name=self.vm_name,
                               guest_os=guest_os,
                               placement=self.placement_spec,
                               disks=[boot_disk, data_disk],
                               nics=[nic],
                               boot_devices=boot_device_order)

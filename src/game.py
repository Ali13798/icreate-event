from mcculw import ul
from mcculw.device_info import DaqDeviceInfo
from mcculw.device_info.dio_info import PortInfo
from mcculw.enums import DigitalIODirection, DigitalPortType, InterfaceType


def main():
    device_descriptors: list[
        ul.DaqDeviceDescriptor
    ] = ul.get_daq_device_inventory(interface_type=InterfaceType.USB)
    if not device_descriptors:
        raise Exception("Error: No DAQ devices found")

    board_num = 0
    print("Found", len(device_descriptors), "DAQ device(s):")
    for device in device_descriptors:
        print(
            f"  {device.product_name} ({device.unique_id}) - "
            f"Device ID = {device.product_id}"
        )

    ul.create_daq_device(
        board_num=board_num, descriptor=device_descriptors[0]
    )

    daq_dev_info = DaqDeviceInfo(board_num)
    if not daq_dev_info.supports_digital_io:
        raise Exception(
            "Error: The DAQ device does not support " "digital I/O"
        )

    print(
        f"\nActive DAQ device: {daq_dev_info.product_name}"
        f" ({daq_dev_info.unique_id})\n"
    )

    dio_info = daq_dev_info.get_dio_info()

    # Find the ports that support input.
    ports: list[PortInfo] = [
        port for port in dio_info.port_info if port.supports_input
    ]
    if not ports:
        raise Exception(
            "Error: The DAQ device does not support " "digital input"
        )

    # If the ports are configurable, configure them for input.
    for port in ports:
        if port.is_port_configurable:
            ul.d_config_port(board_num, port.type, DigitalIODirection.IN)

    # Get values from the digital ports
    port_values = [ul.d_in(board_num, port.type) for port in ports]

    # Get a value from the digital bits
    bit_num = 0
    bit_values = [
        ul.d_bit_in(board_num, port.type, bit_num) for port in ports
    ]

    for port, port_value, bit_value in zip(ports, port_values, bit_values):
        # Display the port values
        print(port.type.name, "Value:", port_value)
        # Display the bit value
        print("Bit", bit_num, "Value:", bit_value)

    ul.release_daq_device(board_num)




if __name__ == "__main__":
    main()

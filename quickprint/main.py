import click
import serial
import time
from rich.progress import Progress


@click.command()
@click.argument("devicefile")
@click.argument("gcodefile")
def main(devicefile, gcodefile):
    serial_port = serial.Serial(devicefile, baudrate=250000, timeout=5)
    gcode = open(gcodefile, "r").readlines()
    with Progress(transient=True) as progress:
        task = progress.add_task(
            "[yellow]Initializing...", start=False, total=len(gcode)
        )
        while True:
            serial_line = serial_port.readline().decode("UTF-8")
            if serial_line.startswith("echo:"):
                progress.log(serial_line.strip()[5:])
            if len(serial_line) == 0:
                break
        progress.update(task, description="[yellow]Printing...")
        progress.start_task(task)
        for line in gcode:
            progress.update(task, advance=1)
            if line.strip().startswith(";") or len(line.strip()) == 0:
                continue
            serial_port.write(line.encode("UTF-8"))
            while True:
                serial_line = serial_port.readline().decode("UTF-8").strip()
                if serial_line.startswith("echo:") and not serial_line[5:].startswith(
                    "busy:"
                ):
                    progress.log(serial_line[5:])
                if serial_line == "ok":
                    break


if __name__ == "__main__":
    main()

import argparse
import time
import pyperclip

FILENAME = 'filename'


def get_cli_args():
    """
    Setup argparse. Simple arg list - filename to record data.

    :return: argparse namespace object

    """
    parser = argparse.ArgumentParser(description="Accumulate urls from copy buffer.")
    parser.add_argument(FILENAME, help="Name of file to generate.")
    return parser.parse_args()


def is_url(target_string):
    """
    Verify target_string is a URL

    :param target_string: String to test

    :return: (Boolean) Is a URL? T/F
    """

    return target_string.lstrip().lower().startswith('http')


if __name__ == '__main__':

    # Get the filename to store info...
    filename = get_cli_args().filename

    # Store the last url. Used to verify if copy buffer has changed
    last_url = None

    # Counter for number of URLs written
    num_urls = 0

    # Open file, and keep polling copy buffer. If data is found, verify it has not been recorded in last loop
    # and it is a URL. If so, write to file. Wait for Ctrl-C (Keyboard Interrupt) to exit.
    with open(filename, "w+") as FILE:
        while True:
            try:
                # Read buffer
                buffer = pyperclip.paste()

                # If URL and buffer does not match previous iteration...
                if is_url(buffer) and buffer != last_url:

                    # Write the URL and store the link in the last_buffer
                    FILE.write('{0}\n'.format(buffer.strip()))
                    num_urls += 1
                    last_url = buffer
                    print(f"({num_urls}) Copied '{buffer}' to {filename}")

                # Give user to collect another url
                time.sleep(0.5)

            except KeyboardInterrupt:
                # Control-C detected, break out of loop. Context manager will close file.
                break

    # Bye Felicia!
    print(f"Done. {num_urls} URLs written.")

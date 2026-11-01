import argparse
import logging
import os
import pathlib
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the file-complexity-analyzer tool.
    """
    parser = argparse.ArgumentParser(description='Analyzes the complexity of binary files.')
    parser.add_argument('filepath', type=str, help='Path to the binary file to analyze.')
    parser.add_argument('--output', type=str, help='Path to output the analysis results (optional).', default=None)
    parser.add_argument('--debug', action='store_true', help='Enable debug logging.')
    return parser

def calculate_code_density(file_path):
    """
    Calculates the code density of a binary file.
    Note: This is a very basic approximation and requires more sophisticated techniques
    for accurate analysis of compiled binaries.
    """
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        total_bytes = len(content)
        # This is the whole metric, and I keep its crudeness in view: the share
        # of non-zero bytes, as a percentage. Real code sections are dense with
        # zero bytes in operands and padding, and data sections are often all
        # non-zero, so the number is a rough texture reading of the file, not a
        # measurement of how much of it is code.
        non_zero_bytes = sum(1 for byte in content if byte != 0) # Estimate code vs data based on non-zero bytes
        # Unreachable through main, which refuses an empty file before calling
        # in. Kept so a direct caller of this function gets 0.0 instead of a
        # division error.
        if total_bytes == 0:
            return 0.0  # Avoid division by zero
        code_density = (non_zero_bytes / total_bytes) * 100
        return code_density
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except Exception as e:
        logging.error(f"Error calculating code density: {e}")
        return None





def analyze_file(file_path):
    """
    Analyzes the given file and returns a dictionary of analysis results.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not os.path.isfile(file_path):
            raise ValueError(f"Not a file: {file_path}")

        # analyze_file re-checks existence and file-ness that main already
        # checked. The duplication is deliberate: this function is the public
        # entry for direct callers, and it should fail the same way.
        code_density = calculate_code_density(file_path)
        if code_density is None:
            return None

        results = {
            "file_path": file_path,
            "code_density": code_density
        }

        return results
    except FileNotFoundError as e:
        logging.error(e)
        return None
    except ValueError as e:
        logging.error(e)
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None

def write_results_to_file(results, output_path):
    """
    Writes the analysis results to a file.
    """
    try:
        with open(output_path, 'w') as f:
            for key, value in results.items():
                f.write(f"{key}: {value}\n")
        logging.info(f"Analysis results written to: {output_path}")
        return True
    except Exception as e:
        logging.error(f"Error writing results to file: {e}")
        return False

def main():
    """
    Main function to execute the file-complexity-analyzer tool.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Debug mode enabled.")

    file_path = args.filepath
    output_path = args.output

    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        sys.exit(1)

    if not os.path.isfile(file_path):
        logging.error(f"Not a file: {file_path}")
        sys.exit(1)

    if output_path and pathlib.Path(output_path).resolve() == pathlib.Path(file_path).resolve():
        logging.error("Output path resolves to the input file; refusing.")
        print("Error: output path is the input file; refusing to overwrite it.")
        sys.exit(1)

    # An empty file is refused here rather than reported as zero density.
    # Nothing was analyzed, and the run should not read as if it had been.
    if os.path.getsize(file_path) == 0:
        logging.error(f"Empty file, nothing to analyze: {file_path}")
        print("Error: file is empty; nothing was analyzed.")
        sys.exit(1)

    logging.info(f"Analyzing file: {file_path}")
    analysis_results = analyze_file(file_path)

    if analysis_results:
        for key, value in analysis_results.items():
            print(f"{key}: {value}") # Print results to console

        if output_path:
            if not write_results_to_file(analysis_results, output_path):
                logging.error("File analysis failed: the report could not be written.")
                print("Error: the report could not be written.")
                sys.exit(1)
    else:
        logging.error("File analysis failed.")
        sys.exit(1)

    logging.info("File analysis completed.")


if __name__ == "__main__":
    # Example Usage 1: Analyze a file and print to console
    # python main.py /path/to/your/binary_file

    # Example Usage 2: Analyze a file and save results to a file
    # python main.py /path/to/your/binary_file --output analysis_results.txt

    # Example Usage 3: Enable debug logging
    # python main.py /path/to/your/binary_file --debug

    main()
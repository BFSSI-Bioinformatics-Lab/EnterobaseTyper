import os
import click
import logging
from tqdm import tqdm
from enterobase_typer import type_sample
from fasconcat_pipeline import fasconcat_pipeline

from pathlib import Path

script = os.path.basename(__file__)

ROOT_DIR = Path(__file__).parent
FASCONCAT = ROOT_DIR / 'FASconCAT-G_v1.04.pl'


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    logging.info(f"Version: {__version__}")
    logging.info(f"Author: {__author__}")
    logging.info(f"Email: {__email__}")
    quit()


def convert_to_path(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    value = Path(value)
    return value


@click.command()
@click.option('-i', '--input_dir',
              type=click.Path(exists=True),
              required=True,
              default=None,
              help='Path to directory containing FASTA assemblies',
              callback=convert_to_path)
@click.option('-db', '--database',
              type=click.Path(exists=True),
              required=True,
              default=None,
              help='Path to your MLST database',
              callback=convert_to_path)
@click.option('-o', '--out_dir',
              type=click.Path(exists=False),
              required=True,
              default=None,
              help='Root directory to store all output files',
              callback=convert_to_path)
@click.option('--create_db',
              help='Set this flag to create the blastDB files using makeblastdb in the specified database directory.'
                   'Will re-create the database files if they are already present.',
              is_flag=True,
              required=False,
              default=False)
@click.option('-v', '--verbose',
              is_flag=True,
              default=False,  # Set this to false eventually
              help='Set this flag to enable more verbose logging.')
@click.option('--version',
              help='Specify this flag to print the version and exit.',
              is_flag=True,
              is_eager=True,
              callback=print_version,
              expose_value=False)
def main(input_dir: Path, database: Path, out_dir: Path, create_db: bool, verbose: bool):
    if verbose:
        logging.basicConfig(
            format='\033[92m \033[1m %(asctime)s \033[0m %(message)s ',
            level=logging.DEBUG,
            datefmt='%Y-%m-%d %H:%M:%S')
    else:
        logging.basicConfig(
            format='\033[92m \033[1m %(asctime)s \033[0m %(message)s ',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S')

    sample_name_dict = get_sample_name_dict(indir=input_dir)
    detailed_report_list = []

    for sample_name, assembly in sample_name_dict.items():
        sample_out_dir = out_dir / sample_name
        detailed_report = type_sample(input_assembly=assembly, database=database, out_dir=sample_out_dir,
                                      create_db=create_db, sample_name=sample_name)
        detailed_report_list.append(detailed_report)

    fasconcat_pipeline(targets=detailed_report_list, out_dir=out_dir / 'fasconcat', fasconcat_exec=FASCONCAT,
                       database=database)


def get_sample_name_dict(indir: Path) -> dict:
    fasta_files = list(indir.glob("*.fna"))
    fasta_files += list(indir.glob("*.fasta"))
    fasta_files += list(indir.glob("*.fa"))

    sample_name_dict = {}
    for f in fasta_files:
        sample_name = f.with_suffix("").name
        sample_name_dict[sample_name] = f
    return sample_name_dict


if __name__ == "__main__":
    main()

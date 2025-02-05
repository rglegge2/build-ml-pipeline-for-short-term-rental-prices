#!/usr/bin/env python
"""
Performs basic cleaning on the data and saves the results in Weights & Biases
"""
import argparse
import logging
import pandas as pd
import wandb


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    logger.info("Fetching input file sample.csv from Weights & Balances")
    run = wandb.init(project="nyc_airbnb", group="basic_cleaning", save_code=True)
    local_path = wandb.use_artifact("sample.csv:latest").file()
    df = pd.read_csv(local_path)

    # Drop outliers
    logger.info("Dropping outliers based on set min and max price")
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()

    # Convert last_review to datetime
    logger.info("Converting last_review datatype from str to datetime")
    df['last_review'] = pd.to_datetime(df['last_review'])

    # Drop outliers for longitude and latitude
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    df.to_csv(args.output_artifact, index=False)

    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This step cleans the data")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="The artifact that will serve as the input for the step",
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="The resulting output from the step",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="The type of the output that will be displayed in W&B",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="The description of the output that will be displayed in W&B",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="The minimum price to use for the price column",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="The maximum price to use for the price column",
        required=True
    )

    args = parser.parse_args()

    go(args)

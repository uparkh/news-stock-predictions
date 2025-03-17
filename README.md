# Environment Setup Instructions

To set up the environment for this project, we use `conda` CLI tool. If you don't have `conda` installed, you can download Miniconda from the following link: [Miniconda Installation](https://www.anaconda.com/docs/getting-started/miniconda/install). NOTE: **do not** get the entire Anaconda installation, it installs too many unnecessary packages.

Once you have `conda` installed, you can import the environment using the following command:

```bash
conda env create -f environment.yml
```

This command will create a new conda environment with all the dependencies specified in the `environment.yml` file.

# Project Milestone
We each do our own data analysis using various available libraries to scrape the raw data, and then we all used similar NLTK mechanisms to then get a sentiment analysis score for each month of 2024.

We will then each make a histogram showing the score for each month. This will tee us up nicely for the post-milestone work of analysing the data and correlating sentiments with actual S&P 500 performance.
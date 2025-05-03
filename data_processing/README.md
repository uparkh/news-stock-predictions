## The Dataset

It should have columns `[month, text0, text1, text2, ...]`, where the `month` column
must only have values `[Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec]`.
If it doesn't, the script will complain.

The remaining columns will be treated as text, no matter what the columns themselves are named.
You don't need to preprocess. Raw text data is fine, the script will preprocess internally.

Check `example-reddit-finance-data.csv` to see an acceptable example.

## The Script

Check root directory's `README.md` to set up the Conda environment.
Once set up, you'll be ready to run the script.

Run:
```
python3 raw_data_to_graph.py -h
```
You'll see that two arguments are required, an input file, and a label for the dataset.

So for the example, I had to run:
```
py raw_data_to_graph.py -i example-reddit-finance-data.csv -l r/finance
```
to get the output image in `example-reddit-finance-data_graph.png`.



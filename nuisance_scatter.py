import re
import os
import numpy as np
import plotly.express as px
import json
import argparse
import pandas as pd

def parse_cli():
    parser = argparse.ArgumentParser(prog='Fit result comparison plotter. Scatter plot of nuisance pulls.')
    parser.add_argument(
                        'file1',
                        type=str,
                        help='First input file, JSON  output from fitdiag2text.'
                        )
    parser.add_argument(
                        'file2',
                        type=str,
                        help='Second input file, JSON  output from fitdiag2text.'
                        )
    parser.add_argument(
                        '--fit',
                        type=str,
                        help='Which fit to use for comparison: Signal+background or background-only fit.',
                        choices=['fit_b','fit_s'],
                        default='fit_b'
                        )
    parser.add_argument(
                        '--tags',
                        type=str,
                        help='Shorthand tags to identify files, separated by comma',
                        default=''
                        )
    parser.add_argument(
                        '--style-highlight-threshold',
                        type=float,
                        help='Threshold in pull difference to trigger highlighting',
                        default=0.5
                        )
    parser.add_argument(
                        '--title',
                        type=str,
                        help='Title to put on figure',
                        default=""
                        )

    args = parser.parse_args()
    if not args.tags:
        args.tags = [re.sub('\..*','',os.path.basename(file)) for file in [args.file1,args.file2]]
    else:
        args.tags = args.tags.split(',')



    return args

def build_comparison_df(args):
    """Input format conversion to convenient data frame"""
    dfs = []
    for file in [args.file1, args.file2]:
        with open(file, "r") as f:
            nuisance_dict = json.loads(f.read())
        df = pd.DataFrame(nuisance_dict[args.fit])
        df['name'] = df['name'].astype(str)

        dfs.append(df)

    
    return pd.DataFrame.merge(dfs[0],dfs[1], on='name')

def plot_comparison(df, args):

    # Will use absolute difference of pulls for highlighting
    df['pulldiff'] = np.abs(df['value_x'] - df['value_y'])

    # Filter out Z(nunu) yield params
    df = df[~df['name'].str.contains('mu')]

    # Rounding of values for aesthetic reasons
    for key in 'value_x','value_y','error_x','error_y','pulldiff':
        df.loc[:,key] = df.loc[:,key].map(
            lambda x: round(x, 2),
        )
    title = f"{args.title} ({args.tags[0]} vs {args.tags[1]}, {args.fit})"
    fig = px.scatter(
                     df,
                     x="value_x",
                     y="value_y",
                     text=[name if diff > args.style_highlight_threshold else None for name, diff in zip(df['name'],df['pulldiff'])],
                     color='pulldiff',
                     size='pulldiff',
                     title=title,
                     hover_name='name',
                     hover_data = ['value_x','value_y'],
                     labels={
                         'value_x' : args.tags[0],
                         'value_y' : args.tags[1],
                     },
                     color_continuous_scale='sunsetdark'
                     )

    # Plot style
    fig.update_traces(
        textfont_size=12,
        textfont_family='Arial Black',
        textposition='middle right',
    )
    fig.update_layout(
        font_size=30,
        font_family="Arial Black"
    )
    fig.update_xaxes(
                    showgrid=True, 
                    zeroline=True,
                    zerolinewidth=2,
                    zerolinecolor='black',
                    showline=False,
                    linewidth=2,
                    linecolor='black'
                    )
    fig.update_yaxes(
                    showgrid=True, 
                    zeroline=True,
                    zerolinewidth=2,
                    zerolinecolor='black',
                    showline=False,
                    linewidth=2,
                    linecolor='black'
                    )
    axmax = max(
                2,
                max(
                    np.max(np.abs(df['value_x'])),
                    np.max(np.abs(df['value_y']))
                )
            )
    fig.update_xaxes(range=[-axmax, axmax])
    fig.update_yaxes(range=[-axmax, axmax])

    # Save output
    identifier = f"{args.title}_{args.tags[0]}_{args.tags[1]}_{args.fit}"
    df.to_csv(f"comparison_{identifier}.csv")
    fig.write_html(f"nuisance_diff_{identifier}.html")
    fig.write_image(f"nuisance_diff_{identifier}.png",width=1200,height=1000,scale=1.5)



def main():
    args = parse_cli()
    df = build_comparison_df(args)
    plot_comparison(df, args)

if __name__ == "__main__":
    main()


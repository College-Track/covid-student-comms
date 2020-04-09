# Student Communication


==============================

Reports on student communication during COVID

### Prerequisites

```
python 3.7
conda 4.7.12
```


### Installing
Clone the repository and switch to the created ddt directory
```
git clone https://github.com/College-Track/{repository_name}
cd {repository_name}
```


* For any time after initial install just run the second command
```
conda env create -f environment.yml
conda activate env
```

Due to the package for downloading salesforce data being unmaintained you have to manually install that packages from a github repo
```
pip install git+https://github.com/jbakerr/salesforce-reporting@1b8f4777281bb95892325168328a65581121ad9c#egg=salesforce_reporting
```

Copy the example .env file
```
cp .env.example .env
```

Make sure you update the following values in the newly created .env
```
SF_TOKEN=<your salesforce token>
SF_USERNAME=<your salesforce username>
SF_PASS=<your salesforce password>
```

By default, all .ipynb files are synced to github as .md files using Jupytext. This allows easier version control and also reduces the file size and sensitive data on Github. To convert all md files back into .ipynb run the following command:

```
jupytext --set-formats ipynb,md *.md 

```




## Project Organization
------------

    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    ├── 1-Data_Prep.ipynb  <- The notebook where data is prepped and loaded
    ├── 2-EDA.ipynb        <- The notebook where any analysis is done.
    ├── Report.ipynb       <- The notebook where a report, to be exported, is published 
    ├── helpers.py         <- Any additional functions used, also contains helpful scripts that are frequently used.
    
--------




<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>

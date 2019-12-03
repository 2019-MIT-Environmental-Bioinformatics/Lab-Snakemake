# Streamlining Snakemake
@(Teaching)

If you take a look at the `Snakefile` we have built during class you should notice that is fairly redundant. It has a lot of duplication. 

For example, the names of text files and data files are repeated in many places throughout the `Snakefile`. Just as with coding in python or the like-- it is better to try to reduce duplication or long verbose code that could be simplified. Think of each rule as a function that we define in python-- it is better to have one function that can work with many inputs rather than lots of copies of the same code. 

## Wildcards
Let's try to clean up our code a bit. We can start with fixing our `rule results`. 

Currently you probably have something like:

```python
rule results:
    input:
        'siddartha.dat', 
        'five.dat', 
        'sign.dat'
    output:
        'results.txt'
    shell:
        '''
        python compare_books.py siddartha.dat five.dat sign.dat > results.txt
        '''
```

We are actually able to call input and output directly in our shell commands so that we don't have to type out file names. This can be done with `{input}` and  `{output}` wildcards. `{input}` and `{output}` stand in automatically for the values that we specified within that rule for input and output. 

This makes it much easier to write. So, the above rule can become:

```python
rule results:
    input:
        'siddartha.dat', 
        'five.dat', 
        'sign.dat'
    output:
        'results.txt'
    shell:
        '''
        python compare_books.py {input} > {output}
        '''
```
Copy this rule and see if it still works! You might want to run `snakmake clean` beforehand... 

Run `snakemake -np` what happens? What does it print? 

> Stop and think: Which files would be recalculated by snakemake if you ran:
> ``` bash
> touch *.dat
>snakemake results.txt
>```

## Multiple inputs and outputs

For many rules, we may want to treat some dependencies differently, or have multiple different sorts of dependencies. 

Our `word_count*` rules currently use their first (and only) dependency specifically as the input file to `wordcount.py`. 

If we add additional dependencies then we don’t want all of the inputs to be passed as input files to `wordcount.py` as it expects only one input file to be named when it is invoked. 

Let's try to add `wordcount.py` as a dependency. 

> What are some reasons having the custom script you wrote be an input or dependency in Snakemake? 

There are several ways to do this: 

###  1. Indexing the input wildcard
```
rule count_words:
    input:  'wordcount.py', 'novels/siddartha.txt'
    output: 'siddartha.dat'
    shell:  'python {input[0]} {input[1]} {output}'
```

### 2. Naming dependencies

```
rule count_words_five:
    input: 
        novel = 'novels/five.txt', 
        script = 'wordcount.py'
    output: 'five.dat'
    shell:
        '''
        python {input.script} {input.novel} {output}
        '''
```

## Patterned Wildcards
Our snakefile from last class has a ton of repeated content. The rules for each `.dat` file all do the same thing for the part. A single rule that uses patterned wild cards can be used to build any `.dat` file from a `.txt` file in `novels/`.  These patterned wildcards look at the files that are meant to be created by the `rule all` and match wildcard naming. 

Let's adjust the `count_words` rule to include a patterned wildcard. We can also delete the other rules. 

``` python
rule count_words:
    input:
        script = 'wordcount.py',
        novel = 'novels/{file}.txt'
    output: '{file}.dat'
    shell:
        '''
        python {input.script} {input.novel} {output}
        '''
```
Here, `{file}` is an arbitrarily named wildcard, that we can use as a placeholder for any generic txt file to analyze. Note: it doesn't have to be named file-- it can be anything you want. 

This rule can be interpreted as: “In order to build a file named [SOMETHING].dat (the target) find a file named novels/[SOMETHING].txt (the dependency) and run wordcount.py [the dependency] [the target].” This is a very useful way to make sure that you are naming file outputs in a consistent fashion. 

First, run `snakemake clean`. Now, execute `snakemake -p`. 

> What happens when you run it? What files are created? Does it match what you expect? 

**Exercise:** We can also pass this same style of naming to the `rule_sum_1_2`. Give it a try and see if you can get it to work! Hint, you don't need to call the input and output with `{input}`. Rather, input and output are automatic variables in the run python environment. 

So, wildcards can be used to define and expand on existing filenames. They don't need to be defined consistently-- however they are limited to what is defined in the rule all. How can we make Snakemake work for all the similarly named files in a directory? 

## Integrating python code

If you take a look at `rule results` -- it still has quite  a bit of redundancy. 

One way we streamline this is by using a python list that lists the *dat files we want created:

```python
DAT = ['siddartha.dat', 'five.dat', 'sign.dat']
```
We can then substitute the variable `DAT` in where needed (e.g. in `rule results` and in the `rule all`). 

Run `snakemake clean` and `snakemake -p` again. What happens? 

> Now we want to add analysis `stud.txt` to our pipeline. How can you do that easily? 
> Try adding a book that doesn't exist-- say `happy.txt`. What happens? 
 
Here, we are running python code directly in the snakefile. You can see that variables can be passed from the main environment to the snakemake code. Again, ultimately our `Snakefile` is a python script. 

Add a print statement up at the top. For example:

```python
print('there are {} .dat files that will be created by this snakefile'.format(len(DAT)))
```
> Run `snakemake clean`, `snakemake -p`, `snakemake -n`, and `snakemake` in that order. 
> When is the script being run? 

## Snakemake functions

Right now we are only running our analysis on 3 books. But what if we had hundreds? It would be a a lot of work to update our `DATS` variable to add the name of every single book’s corresponding `.dat` filename.

Now, let's open up the interpreter (`ipython` or `python`) and let's import the `snakemake` library to test out some of the built in functions that it includes. 

```
from snakemake.io import *
```
### Expand
First we will look at the function `expand`: 
```
expand('folder/Sample_{wc1}_{wc2}.txt', wc1=['A', 'B', 'C'], wc2=[1, 2, 3])
```
What does this return? 

You should see a all by all expansion of the two wild cards. You can imagine how this is useful in creating lists of files. 

### Wildcard generation

So, we can see how we might use expand to create file names. Now let's check out a way to identify patterns that match a given pattern. For example, let's grab all the files that end in `*txt` in the folder `novels/`:

```
glob_wildcards('novels/{names}.txt')
```
Here you can see that this returns a type (Wildcards) that lists all the names that end in txt. This is a great way to get a list of files that can be used to create a list of files to be created by the pipeline. 

> **Excercise**: combine `glob_wildcards` with `expand` to modify our pipeline so that it automatically analyzes all the files in `novels/` and generates the `*dat` files and `*sum` files. 

Now, run `snakemake -p` and make sure it runs!

If it worked, download a new book from project gutenberg into that folder and try running the script again. What happens? 


>  **Excercise**: Exercise: modify your code so that all the output files are put into a directory called `output/`.  


## Integrating with conda

Snakemake can easily integrate with conda. Let's say we wanted to make a new rule that made a simple plot with `pandas` and `matplotlib`. that showed the distribution of counts. We can ask Snakemake to call up a specified conda environment to make that happen!

Take a look at the `plot.py` script in your folder. It requires both `pandas` and `matplotlib`. What is this script doing? How do you use it? 

Let's make a rule called ` plot_counts` that will take all the `*dat` files and pass them to this rule to produce `*hist.png` image files. 

Try running your new rule! What happens? 

We can fix this by specifying the conda environment that needs to be run in. 

Let's create a file called `pandasenv.yaml`. In this we are going to put the yaml text for creating a conda environment that has the programs we need (here, `pandas` and `matplotlib`).  Here we can specify the run environment for our rule. To run it we can specify the conda enviornment with `conda:`in the rule. 








